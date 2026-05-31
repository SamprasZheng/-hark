"""One-shot: audit the bot's view/send/embed permission + wired message-function
in EVERY text channel of the guild — i.e. confirm `!cmd` and the channel
functions can actually execute everywhere the bot can post.

`!cmd` / `!help` is handled in on_message for ANY channel, but it can only REPLY
where the bot has View Channel + Send Messages. This prints that per channel
(plus the special routing wired by name) and writes a UTF-8 JSON report.

    python -m_or_file scripts/discord_audit.py
"""

from __future__ import annotations

import json

import discord

from sharks.discord import config as C
from sharks.discord.config import Settings


def _func(name: str) -> str:
    if name == C.CH_ASK:
        return "ASK loopback (=/ask, 打字即問 Claude)"
    if name == C.CH_COUNCIL:
        return "PERSONA chat (打『huang: …』)"
    if name == C.CH_GENERAL:
        return "CHATTER 速解讀 + !cmd"
    if name in (C.CH_MORNING, C.CH_NOON, C.CH_EVENING):
        return "MEETING 自動貼文 + !cmd"
    return "!cmd / slash 指令"


def main() -> int:
    s = Settings.load()
    if not s.token:
        print("DISCORD_BOT_TOKEN empty")
        return 1
    intents = discord.Intents.default()
    intents.members = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:  # pragma: no cover - network
        try:
            g = (client.get_guild(s.guild_id) if s.guild_id else None) \
                or (client.guilds[0] if client.guilds else None)
            report = {"guild": g.name if g else None, "channels": []}
            if g:
                me = g.me
                for ch in g.text_channels:
                    p = ch.permissions_for(me)
                    report["channels"].append({
                        "name": ch.name,
                        "category": ch.category.name if ch.category else None,
                        "view": p.view_channel,
                        "send": p.send_messages,
                        "embed": p.embed_links,
                        "cmd_ok": bool(p.view_channel and p.send_messages),
                        "func": _func(ch.name),
                    })
            out = C.PROJECT_ROOT / "outputs" / "discord-channel-audit.json"
            out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            ok = sum(1 for c in report["channels"] if c["cmd_ok"])
            print(f"guild={report['guild']!r} channels={len(report['channels'])} cmd_ok={ok}")
            print(f"report={out}")
            for c in report["channels"]:
                flag = "OK " if c["cmd_ok"] else "NO!"
                print(f"  {flag} v={int(c['view'])} s={int(c['send'])} e={int(c['embed'])} "
                      f"| {ascii(c['name'])} | {ascii(c['func'])}")
        finally:
            await client.close()

    client.run(s.token, log_handler=None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
