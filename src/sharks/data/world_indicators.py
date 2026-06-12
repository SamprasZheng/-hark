"""GSCPI / GPR 世界指標客戶端 — 供應鏈壓力 + 地緣政治風險(world model Layer 1).

Sources(皆免 key,grade A primary):
  GSCPI — NY Fed Global Supply Chain Pressure Index(月度,本身即全史 z-score 單位):
    https://www.newyorkfed.org/medialibrary/research/interactives/gscpi/downloads/gscpi_data.xlsx
    (副檔名是 .xlsx 但 payload 是 legacy BIFF .xls — 2026-06-12 實測確認)
  GPR — Caldara & Iacoviello Geopolitical Risk index(月度 + 每日):
    https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls
      (月度,115 欄,含國家分項 GPRC_TWN / GPRC_CHN;基準 ~100)
    https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls
      (每日,GPRD + GPRD_MA30/MA7,約 1-3 天滯後)

傳輸走 stdlib urllib + fred_client 同款 retry/backoff 紀律(429 看 Retry-After、
5xx/transport 指數退避、非 429 4xx 立即 fatal、耗盡丟 :class:`WorldDataError`)。
解析需要 ``xlrd``(BIFF 無法用 stdlib 解)— lazy import,模組本身無依賴即可載入;
安裝:``pip install -e ".[world]"``。

Point-in-time(philosophy/09):每列帶 ``as_of_timestamp``(觀測日 — 值是「為了」
哪一天)與 ``source_first_visible_at``(live 路徑為 None:兩個來源每次發布都
就地修訂全史、無 vintage 檔案庫)。要建立本地前向 vintage 史,world_monitor 會把
每日解析後的序列存到 ``data/lake/world/`` — 見 regime/world_monitor.py。
"""

from __future__ import annotations

import time
import urllib.error
import urllib.request
from typing import Optional

GSCPI_URL = ("https://www.newyorkfed.org/medialibrary/research/interactives/"
             "gscpi/downloads/gscpi_data.xlsx")
GPR_MONTHLY_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls"
GPR_DAILY_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
DEFAULT_USER_AGENT = "sharks-world/0.1 (+https://github.com/SamprasZheng)"

GSCPI_SHEET = "GSCPI Monthly Data"
GPR_MONTHLY_COLS = ("GPR", "GPRT", "GPRC_TWN", "GPRC_CHN")
GPR_DAILY_COLS = ("GPRD", "GPRD_MA30", "GPRD_MA7")


class WorldDataError(RuntimeError):
    """Raised when a world-indicator source cannot be fetched/parsed after retries."""


def _retry_after_seconds(exc) -> Optional[float]:
    hdrs = getattr(exc, "headers", None) or getattr(exc, "hdrs", None)
    if hdrs is None:
        return None
    try:
        val = hdrs.get("Retry-After")
    except Exception:
        return None
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _request_bytes(
    url: str,
    *,
    opener=None,
    max_retries: int = 4,
    timeout: float = 60.0,
    base_backoff: float = 1.5,
    sleep=time.sleep,
) -> bytes:
    """GET ``url`` → raw bytes(xls),retry 紀律同 fred_client。opener 可注入。"""
    opener = opener or urllib.request.urlopen
    last_err = None
    for attempt in range(max_retries):
        req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
        try:
            with opener(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                last_err = "http 429 (rate limited)"
                delay = _retry_after_seconds(exc)
                if delay is None:
                    delay = base_backoff * (2 ** attempt)
            elif 500 <= exc.code < 600:
                last_err = f"http {exc.code}"
                delay = base_backoff * (2 ** attempt)
            else:
                raise WorldDataError(f"world-data HTTP {exc.code} for {url}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = f"transport ({getattr(exc, 'reason', exc)})"
            delay = base_backoff * (2 ** attempt)
        if attempt < max_retries - 1:
            sleep(delay)
    raise WorldDataError(
        f"world-data fetch failed after {max_retries} attempts ({last_err}): {url}"
    )


def _sheet_grid(xls_bytes: bytes, sheet_name: Optional[str] = None) -> list[list]:
    """BIFF .xls → 純值網格(日期 → 'YYYY-MM-DD' 字串、空格 → None)。

    這是唯一碰 xlrd 的地方;下游解析全是純函式(grid in → series out),
    測試餵合成 grid 即可離線。
    """
    try:
        import xlrd
    except ImportError as exc:                                     # pragma: no cover
        raise WorldDataError(
            "xlrd not installed — pip install -e \".[world]\" (BIFF .xls 解析需要)"
        ) from exc
    book = xlrd.open_workbook(file_contents=xls_bytes)
    try:
        sheet = book.sheet_by_name(sheet_name) if sheet_name else book.sheet_by_index(0)
    except Exception as exc:
        raise WorldDataError(f"sheet not found: {sheet_name!r}") from exc
    grid: list[list] = []
    for i in range(sheet.nrows):
        row = []
        for j in range(sheet.ncols):
            c = sheet.cell(i, j)
            if c.ctype == xlrd.XL_CELL_DATE:
                row.append(xlrd.xldate.xldate_as_datetime(
                    c.value, book.datemode).strftime("%Y-%m-%d"))
            elif c.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK, xlrd.XL_CELL_ERROR):
                row.append(None)
            else:
                row.append(c.value)
        grid.append(row)
    return grid


# ── 純解析(grid → series;無 I/O)──

def _find_header(grid: list[list], required: tuple[str, ...]) -> Optional[tuple[int, dict]]:
    """前 30 列中找齊 required 欄名的表頭列 → (row_idx, {欄名: col_idx})。"""
    for i, row in enumerate(grid[:30]):
        names = {str(v).strip(): j for j, v in enumerate(row) if isinstance(v, str)}
        if all(r in names for r in required):
            return i, names
    return None


_MONTHS = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05",
           "jun": "06", "jul": "07", "aug": "08", "sep": "09", "oct": "10",
           "nov": "11", "dec": "12"}


def _norm_date(v) -> Optional[str]:
    """cell 值 → 'YYYY-MM-DD' 或 None。容兩種真實形狀:ISO(xls 日期 cell 已轉)
    與 NY Fed 的文字日期 '31-Jan-1998'(GSCPI 把日期存成字串,非日期 cell)。"""
    if not isinstance(v, str):
        return None
    s = v.strip()
    if len(s) >= 10 and s[:4].isdigit():                  # ISO
        return s[:10]
    parts = s.split("-")
    if len(parts) == 3 and parts[2].isdigit() and len(parts[2]) == 4:
        mm = _MONTHS.get(parts[1][:3].lower())
        if mm and parts[0].isdigit():
            return f"{parts[2]}-{mm}-{int(parts[0]):02d}"
    return None


def parse_series_grid(grid: list[list], date_col: str,
                      value_cols: tuple[str, ...]) -> dict[str, list[tuple[str, float]]]:
    """網格 → {欄名: [(date, value), ...]}。純函式;非數值/壞日期列直接跳過,
    絕不發明值(NY Fed 表頭夾雜說明列,靠日期形狀過濾)。"""
    hit = _find_header(grid, (date_col, *value_cols))
    if not hit:
        return {}
    hi, names = hit
    out: dict[str, list[tuple[str, float]]] = {c: [] for c in value_cols}
    for row in grid[hi + 1:]:
        di = names[date_col]
        dt = _norm_date(row[di] if di < len(row) else None)
        if dt is None:
            continue
        for c in value_cols:
            ci = names[c]
            v = row[ci] if ci < len(row) else None
            if isinstance(v, (int, float)):
                out[c].append((dt[:10], float(v)))
    return out


def _stamp(series_id: str, pairs: list[tuple[str, float]]) -> list[dict]:
    """PIT 戳記(data/__init__.py 契約):as_of=觀測日;first_visible=None(live 修訂序列)。"""
    return [{"series_id": series_id, "date": d, "value": v,
             "as_of_timestamp": d, "source_first_visible_at": None}
            for d, v in pairs]


# ── fetchers ──

def fetch_gscpi(*, opener=None, sleep=time.sleep, max_retries: int = 4,
                timeout: float = 60.0) -> list[dict]:
    """GSCPI 月度全史 → PIT 列(單位=全史 z-score,NY Fed 定義)。"""
    from sharks.data.call_log import timed_call
    with timed_call("nyfed", "gscpi-xls"):
        raw = _request_bytes(GSCPI_URL, opener=opener, sleep=sleep,
                             max_retries=max_retries, timeout=timeout)
    series = parse_series_grid(_sheet_grid(raw, GSCPI_SHEET), "Date", ("GSCPI",))
    return _stamp("GSCPI", series.get("GSCPI") or [])


def fetch_gpr_monthly(columns: tuple[str, ...] = GPR_MONTHLY_COLS, *, opener=None,
                      sleep=time.sleep, max_retries: int = 4,
                      timeout: float = 120.0) -> dict[str, list[dict]]:
    """GPR 月度(1900+)→ {欄名: PIT 列}。GPRC_* 為該國占比分項(量綱 ≪ GPR 本體)。"""
    from sharks.data.call_log import timed_call
    with timed_call("iacoviello", "gpr-monthly-xls"):
        raw = _request_bytes(GPR_MONTHLY_URL, opener=opener, sleep=sleep,
                             max_retries=max_retries, timeout=timeout)
    series = parse_series_grid(_sheet_grid(raw), "month", columns)
    return {c: _stamp(c, pairs) for c, pairs in series.items()}


def fetch_gpr_daily(columns: tuple[str, ...] = GPR_DAILY_COLS, *, opener=None,
                    sleep=time.sleep, max_retries: int = 4,
                    timeout: float = 120.0) -> dict[str, list[dict]]:
    """GPR 每日(1985+,約 1-3 天滯後)→ {欄名: PIT 列}。"""
    from sharks.data.call_log import timed_call
    with timed_call("iacoviello", "gpr-daily-xls"):
        raw = _request_bytes(GPR_DAILY_URL, opener=opener, sleep=sleep,
                             max_retries=max_retries, timeout=timeout)
    series = parse_series_grid(_sheet_grid(raw), "date", columns)
    return {c: _stamp(c, pairs) for c, pairs in series.items()}
