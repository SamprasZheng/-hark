"""Screen/Finviz slash commands, registered onto an existing bot tree.

Self-contained add-on so the screens layer (basecross / rally / stealth / ecomrank /
finviz / guide / playbook) can be wired into bot.py with a single call —
``screen_commands.register(self.tree, self.settings)`` at the end of
``_register_commands`` — without surgically editing the rest of bot.py. All command
code + embeds live here. recommend-only; the bot never trades.
"""

from __future__ import annotations

import asyncio

import discord
from discord import app_commands

from sharks.discord import basecross as _basecross
from sharks.discord.basecross import run_basecross
from sharks.scoring import rally_signal as _rally
from sharks.scoring import stealth_signal as _stealth
from sharks.data import finviz_elite as _finviz

# scope choices shared by /basecross and /rally
_SCOPES = [
    app_commands.Choice(name="2022 殺下來的大底", value="killed2022"),
    app_commands.Choice(name="AI 錯殺軟體股", value="ai_software"),
    app_commands.Choice(name="電商 · agentic-commerce", value="ecommerce"),
    app_commands.Choice(name="小型電商(高賠率)", value="ecommerce_small"),
    app_commands.Choice(name="廣度錯殺(民生/消費/醫療)", value="broadening"),
    app_commands.Choice(name="太空板塊(SpaceX IPO)", value="space"),
    app_commands.Choice(name="跨產業分散轉機股", value="diversified"),
    app_commands.Choice(name="中風險轉機股", value="midrisk"),
    app_commands.Choice(name="2026 IPO 超級年代理", value="ipo"),
    app_commands.Choice(name="Agentic 支付/金融科技", value="payments"),
    app_commands.Choice(name="Web3/加密週期", value="crypto"),
    app_commands.Choice(name="全名單", value="all"),
]


# ── embeds ──────────────────────────────────────────────────────────────────-

def basecross_to_embed(title, rows) -> discord.Embed:
    e = discord.Embed(title=f"📈 月線大底金叉 · {title}",
                      description="月線底部金叉 + 資金介入。找 Boeing/Snowflake 那種大底翻揚。",
                      color=0x8E44AD)
    green = [c for c in rows if c.verdict.startswith("🟢")]
    yellow = [c for c in rows if c.verdict.startswith("🟡")]
    blue = [c for c in rows if c.verdict.startswith("🔵")]
    def line(c):
        if c.last is None:
            return f"`{c.ticker}` — {c.note}"
        th = f" [{c.theme}]" if c.theme else ""
        vs = f" · 量×{c.vol_surge:.1f}" if c.vol_surge else ""
        return f"`{c.ticker}`{th} 距高 {c.dist_ath_pct:.0f}%{vs}"
    if green:
        e.add_field(name="🟢 金叉+資金(主力候選)", value="\n".join(line(c) for c in green)[:1024], inline=False)
    if yellow:
        e.add_field(name="🟡 金叉或量能,待另一半確認", value="\n".join(line(c) for c in yellow)[:1024], inline=False)
    if blue:
        e.add_field(name="🔵 築底中 · 待金叉", value="\n".join(line(c) for c in blue[:12])[:1024], inline=False)
    e.set_footer(text="recommend-only · 月線=日線重抽樣近似 · 盈利 q 需 FOM 宇宙覆蓋")
    return e


def rally_to_embed(title, signals) -> discord.Embed:
    e = discord.Embed(title=f"🚀 起漲訊號追蹤 · {title}",
                      description="融合 資金/技術/消息/供應鏈/基本面;**連續起漲**才『可考慮買入』。",
                      color=0xE74C3C)
    def dimstr(s):
        return " ".join(f"{_rally.DIM_ZH[d]}{int(s.dims[d])}" if s.dims.get(d) is not None
                        else f"{_rally.DIM_ZH[d]}–" for d in _rally.DIMENSIONS)
    def line(s):
        return f"`{s.ticker}` C{s.composite:.0f}/DNA{s.dna_match:.0f} 連{s.streak} · {dimstr(s)}"
    buy = [s for s in signals if s.buy_consider]
    rising = [s for s in signals if s.is_rallying and not s.buy_consider and not s.warning]
    grave = [s for s in signals if s.conviction.startswith("🚫")]
    nofuel = [s for s in signals if s.conviction.startswith("🪨")]
    coil = [s for s in signals if not s.is_rallying and not s.warning and s.composite >= 45]
    if buy:
        e.add_field(name="🟢 連續起漲 · 可考慮買入(分批/小倉)", value="\n".join(line(s) for s in buy)[:1024], inline=False)
    if rising:
        e.add_field(name="🟡 起漲中(觀察,未達連續門檻)", value="\n".join(line(s) for s in rising[:10])[:1024], inline=False)
    if coil:
        e.add_field(name="🔵 蓄勢(尚未起漲)", value="\n".join(line(s) for s in coil[:8])[:1024], inline=False)
    if nofuel:
        e.add_field(name="🪨 缺燃料·反彈非大浪(此 regime 撐不起 — 不追)",
                    value="\n".join(line(s) for s in nofuel[:8])[:1024], inline=False)
    if grave:
        e.add_field(name="🚫 純炒作·無實證(墓園型 — 不追)",
                    value="\n".join(f"`{s.ticker}` {s.warning[:60]}" for s in grave[:6])[:1024], inline=False)
    e.set_footer(text="非2021瘋牛:要真盈利/真題材才成大浪 · 墓園/缺燃料不追 · recommend-only")
    return e


def stealth_to_embed(title, rows) -> discord.Embed:
    e = discord.Embed(title=f"🕵️ 隱蔽吸籌偵測 · {title}",
                      description="找『資金先進、價格還沒動』的吸籌指紋 — 抓還沒炒上去的。recommend-only。",
                      color=0x34495E)
    stealth = [r for r in rows if r.stealth]
    started = [r for r in rows if r.verdict.startswith("🟡")]
    watch = [r for r in rows if r.verdict.startswith("🔵")]
    def line(r):
        cap = f"{r.capital:.0f}" if r.capital is not None else "–"
        d = f"{r.dist_ath_pct:.0f}%" if r.dist_ath_pct is not None else "–"
        return f"`{r.ticker:<5}` 吸籌{r.score:.0f} · 資金{cap}/距高{d}"
    if stealth:
        e.add_field(name="🕵️ 隱蔽吸籌(量進價未動 — 最值得盯)", value="\n".join(line(r) for r in stealth[:14])[:1024], inline=False)
    if started:
        e.add_field(name="🟡 已啟動(量已表態,非隱蔽)", value="\n".join(line(r) for r in started[:10])[:1024], inline=False)
    if watch:
        e.add_field(name="🔵 疑似吸籌(續觀察)", value="\n".join(line(r) for r in watch[:8])[:1024], inline=False)
    e.set_footer(text="資金先進、價未動 · regime-conditional:資金面 STRESS 小股先死 · 非建議")
    return e


def ecomrank_to_embed(rows, small_set) -> discord.Embed:
    e = discord.Embed(title="🏆 綜合排名 · 獲利空間 × 基本面 × 炒作動能",
                      description="基本面35% + 獲利空間35% + 炒作動能30%。先驗會被即時數據覆蓋。recommend-only。",
                      color=0xF1C40F)
    def fmt(v):
        return f"{v:.0f}" if isinstance(v, (int, float)) else "–"
    lines = []
    for i, r in enumerate(rows[:24], 1):
        sz = "小" if r["ticker"] in small_set else "大"
        mom = "待" if r.get("momentum_pending") else fmt(r.get("momentum"))
        lines.append(f"{i:>2} `{r['ticker']:<5}` 綜{r['composite']:>4.0f} · "
                     f"基{fmt(r.get('fundamental'))}/空{fmt(r.get('upside'))}/動{mom} [{sz}]")
    chunk, n = [], 0
    for ln in lines:
        if n + len(ln) + 1 > 1000 and chunk:
            e.add_field(name="排名", value="\n".join(chunk), inline=False)
            chunk, n = [], 0
        chunk.append(ln); n += len(ln) + 1
    if chunk:
        e.add_field(name="排名(續)" if e.fields else "排名", value="\n".join(chunk), inline=False)
    e.set_footer(text="先驗(被 FOM/即時覆蓋)· 動能=basecross 即時 · 非個人化建議")
    return e


def guide_embed() -> discord.Embed:
    e = discord.Embed(title="🧭 操作導覽(事件 → 流程)",
                      description="生產線:你進料(提題材)+ 執行(下單),中間系統跑。手冊 docs/OPERATING_MANUAL.md。",
                      color=0x16A085)
    e.add_field(name="事件出現後的 7 關", value=(
        "0 進料 `/ingest` · 1 研究 `/council` · 2 篩選 `/stealth`→`/basecross`→`/rally`(+`/finviz`)\n"
        "3 品管閘(燃料/regime/墓園,內建)· 4 排程(weekly plan)· 5 執行(你下單)\n"
        "6 記錄閉環(議會回寫+連續起漲)· 7 反饋 `/feedback` `/rescan`"), inline=False)
    e.add_field(name="scope", value="space ipo payments crypto ecommerce ai_software broadening "
                "diversified midrisk killed2022 all · 或 tickers:AAPL,NVDA", inline=False)
    e.set_footer(text="recommend-only · 永不下單")
    return e


def playbook_embed() -> discord.Embed:
    e = discord.Embed(title="🗺️ 作戰儀表板(2026 H2)",
                      description="頂底互換:賣 NVDA 強 → 買錯殺底。分批、信號驅動、留彈藥到九月。"
                                  "非2021、廣度小 → 只買有燃料(真賺錢/真題材)+ 連續起漲。",
                      color=0x1ABC9C)
    e.add_field(name="時間軸", value=(
        "現在→7月 埋伏(/stealth)· Q3 IPO 窗(SNOW/V/MA)· 8月 加碼(/rally)\n"
        "9月 變盤決勝 · Q3–Q4 SpaceX IPO(/basecross space)· 2027H1 AI-PC 換機才引爆"), inline=False)
    e.add_field(name="⏳ 晚期警戒", value="IPO 洪峰+BTC 後段循環+窄廣度=晚期訊號匯聚;吃最後一段、留現金、"
                "把 2027 級回檔當基準。詳見 watchlist/*.md。", inline=False)
    e.set_footer(text="recommend-only · 永不下單")
    return e


# ── registration ──────────────────────────────────────────────────────────--

def register(tree, settings) -> None:
    """Register the screen/finviz slash commands on an existing CommandTree."""

    @tree.command(name="basecross", description="月線底部金叉+資金介入篩選(Boeing/Snowflake 大底)")
    @app_commands.describe(which="題材池", tickers="額外代號,逗號分隔")
    @app_commands.choices(which=_SCOPES)
    async def basecross_cmd(interaction: discord.Interaction,
                            which: app_commands.Choice[str] = None, tickers: str = ""):
        await interaction.response.defer(thinking=True)
        extra = [t.strip().upper() for t in tickers.replace(" ", ",").split(",") if t.strip()]
        title, rows = await asyncio.to_thread(
            run_basecross, which.value if which else "all", settings=settings, extra_tickers=extra or None)
        await interaction.followup.send(embed=basecross_to_embed(title, rows))

    @tree.command(name="rally", description="起漲訊號追蹤(5維融合;連續起漲才可考慮買入)")
    @app_commands.describe(which="題材池", tickers="額外代號")
    @app_commands.choices(which=_SCOPES)
    async def rally_cmd(interaction: discord.Interaction,
                        which: app_commands.Choice[str] = None, tickers: str = ""):
        await interaction.response.defer(thinking=True)
        extra = [t.strip().upper() for t in tickers.replace(" ", ",").split(",") if t.strip()]
        scope = which.value if which else "all"
        title, rows = await asyncio.to_thread(
            run_basecross, scope, settings=settings, extra_tickers=extra or None)
        quality = await asyncio.to_thread(_basecross.quality_from_fom, settings.outputs_dir)
        prior = await asyncio.to_thread(_rally.load_prior_streaks, settings.outputs_dir)
        signals = _rally.build_signals(rows, quality_by_ticker=quality, prior_streaks=prior)
        await asyncio.to_thread(_rally.write_state, settings.outputs_dir, signals)
        await interaction.followup.send(embed=rally_to_embed(scope, signals))

    @tree.command(name="stealth", description="隱蔽吸籌偵測(資金先進、價未動;抓還沒炒上去的)")
    @app_commands.describe(scope="broadening(預設)/all/space/ipo…", tickers="額外代號")
    async def stealth_cmd(interaction: discord.Interaction,
                          scope: str = "broadening", tickers: str = ""):
        await interaction.response.defer(thinking=True)
        extra = [t.strip().upper() for t in tickers.replace(" ", ",").split(",") if t.strip()]
        title, rows = await asyncio.to_thread(
            run_basecross, (scope or "broadening").strip().lower(),
            settings=settings, extra_tickers=extra or None)
        await interaction.followup.send(embed=stealth_to_embed(title, _stealth.stealth_rank(rows)))

    @tree.command(name="ecomrank", description="綜合排名(獲利空間×基本面×炒作動能;動能即時 fold-in)")
    @app_commands.describe(scope="ecommerce(預設)/space/ipo/all…", tickers="額外代號")
    async def ecomrank_cmd(interaction: discord.Interaction,
                           scope: str = "ecommerce", tickers: str = ""):
        await interaction.response.defer(thinking=True)
        extra = [t.strip().upper() for t in tickers.replace(" ", ",").split(",") if t.strip()]
        title, rows = await asyncio.to_thread(
            run_basecross, (scope or "ecommerce").strip().lower(),
            settings=settings, extra_tickers=extra or None)
        quality = await asyncio.to_thread(_basecross.quality_from_fom, settings.outputs_dir)
        ranked = _rally.ecommerce_rank(rows, quality_by_ticker=quality)
        await interaction.followup.send(embed=ecomrank_to_embed(ranked, set(_basecross.ECOMMERCE_SMALL)))

    @tree.command(name="finviz", description="Finviz API 掃描 → 9維 → rally 排名(資金/技術/基本面更精準)")
    @app_commands.describe(filters="preset 或 Finviz f= 過濾字串(預設 dipbuy)",
                           cols="可選:Finviz Custom view 的 c= 欄位字串")
    async def finviz_cmd(interaction: discord.Interaction, filters: str = "dipbuy", cols: str = ""):
        await interaction.response.defer(thinking=True)
        try:
            rows = await asyncio.to_thread(
                _finviz.fetch_screen, filters,
                view=_finviz.DIMENSION_VIEW, columns=(cols or _finviz.DIMENSION_COLUMNS))
        except Exception as exc:
            await interaction.followup.send(f"⚠️ Finviz 掃描失敗:{exc}"[:1900])
            return
        prior = await asyncio.to_thread(_rally.load_prior_streaks, settings.outputs_dir)
        signals = _finviz.signals_from_finviz(rows, prior_streaks=prior)
        await asyncio.to_thread(_rally.write_state, settings.outputs_dir, signals)
        dims = [_finviz.finviz_row_to_dims(r) for r in rows]
        n = len(rows) or 1
        cov = ", ".join(f"{k}{sum(1 for d in dims if d.get(k) is not None)}/{n}"
                        for k in ("technical", "capital", "fundamental"))
        e = rally_to_embed(f"Finviz · {filters}({len(rows)}檔)", signals)
        e.add_field(name="維度覆蓋(Finviz 欄位)",
                    value=f"{cov} — 若多為 0/{n},用 `cols:` 貼你 Custom view 的 c= 字串", inline=False)
        await interaction.followup.send(embed=e)

    @tree.command(name="guide", description="操作導覽:事件→流程的 7 關 + 題材索引")
    async def guide_cmd(interaction: discord.Interaction):
        await interaction.response.send_message(embed=guide_embed(), ephemeral=True)

    @tree.command(name="playbook", description="作戰儀表板:題材 + 時間軸 + 對應指令")
    async def playbook_cmd(interaction: discord.Interaction):
        await interaction.response.send_message(embed=playbook_embed(), ephemeral=True)
