"""Wiki ingest — write knowledge INTO $hark from Discord (mobile-friendly).

Paste text (or a URL) in #知識注入 or use /ingest, and a markdown note lands in
`$hark/wiki/inbox/` with proper frontmatter (type/tags/as_of_timestamp/source),
then the local RAG index is invalidated so /notebook can find it immediately.

This is the WRITE side of the in-Discord local NotebookLM. It only writes NOTES
to a contained inbox; it never trades, never edits curated pages, never
auto-commits to git (the human reviews/commits). A pasted URL is best-effort
fetched (urllib + crude tag-strip) so you can ingest an article from your phone.
"""

from __future__ import annotations

import html
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional

from sharks.discord.config import TPE, Settings

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_URL_RE = re.compile(r"^https?://\S+$", re.IGNORECASE)


def _slug(title: str, now: datetime) -> str:
    base = _SLUG_RE.sub("-", title.lower()).strip("-")[:40]
    if not re.search(r"[a-z0-9]", base):     # Chinese-only title → no ascii slug
        base = "note"
    # microseconds keep rapid back-to-back pastes from colliding on one filename
    return f"{now:%Y-%m-%d-%H%M%S}-{now.microsecond:06d}-{base}"


def _fetch_url(url: str, timeout: int = 15) -> tuple[Optional[str], str]:
    """Best-effort fetch a URL → (title, readable_text). Never raises."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 PolkaSharks"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(800_000).decode("utf-8", "replace")
    except Exception as exc:
        return None, f"(無法抓取 {url}:{exc})"
    tm = re.search(r"<title[^>]*>(.*?)</title>", raw, re.I | re.S)
    title = html.unescape(re.sub(r"\s+", " ", tm.group(1))).strip()[:120] if tm else None
    text = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()
    return title, text[:8000]


def ingest(content: str, *, title: Optional[str] = None, source: str = "discord",
           tags: tuple[str, ...] = (), settings: Optional[Settings] = None) -> dict:
    """Write a note into wiki/inbox/. Returns {ok, path, title, url, chars}."""
    settings = settings or Settings.load()
    now = datetime.now(TPE)
    content = (content or "").strip()
    if not content:
        return {"ok": False, "error": "empty content"}

    url, body = None, content
    if _URL_RE.match(content):
        url = content.split()[0]
        ftitle, ftext = _fetch_url(url)
        title = title or ftitle or url
        body = f"來源網址:{url}\n\n{ftext}"

    if not title:
        first = (content.splitlines()[0].strip() if content else "") or "note"
        title = first[:80]

    inbox = settings.project_root / "wiki" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    path = inbox / f"{_slug(title, now)}.md"
    taglist = ", ".join(("ingested", "discord", *tags))
    front = (
        "---\n"
        "type: note\n"
        f"tags: [{taglist}]\n"
        f"as_of_timestamp: {now.isoformat()}\n"
        "author_role: human\n"
        f"source: {source}\n"
        + (f"url: {url}\n" if url else "")
        + "---\n\n"
        f"# {title}\n\n{body}\n"
    )
    path.write_text(front, encoding="utf-8")

    # invalidate the RAG index so /notebook finds it immediately
    try:
        from sharks.discord import wiki_rag
        wiki_rag._INDEX_CACHE.clear()
    except Exception:
        pass

    return {
        "ok": True,
        "path": str(path.relative_to(settings.project_root)).replace("\\", "/"),
        "title": title,
        "url": url,
        "chars": len(body),
    }


def recent(settings: Optional[Settings] = None, n: int = 10) -> list[str]:
    """Newest ingested note paths (relative), for /recent."""
    settings = settings or Settings.load()
    inbox = settings.project_root / "wiki" / "inbox"
    if not inbox.is_dir():
        return []
    files = sorted(inbox.glob("*.md"), reverse=True)[:n]
    return [str(p.relative_to(settings.project_root)).replace("\\", "/") for p in files]
