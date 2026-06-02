"""Sharks Discord layer — a private notification + conversation + Q&A surface.

This package puts a thin Discord skin on the existing Sharks brain. It does NOT
add any new decision logic and it inherits every hard boundary from the
constitution ([[sharks]]) and CLAUDE.md §2:

  * RECOMMEND-ONLY. Never places trades, never connects to a brokerage/exchange,
    never holds keys. Discord is an output + chat layer, full stop.
  * No auto-writeback. The /ask loopback runs local Claude Code in a READ-ONLY
    research mode; anything that would mutate wiki/ is surfaced for human review,
    never committed by the bot.
  * Private by design. The bot never invites anyone; locking the server to two
    people is a Discord-side setting (see setup_guild.py + README).

Four capabilities, one process:
  1. meetings.py — 晨會 / 晚會 / 週會 digests composed from outputs/.
  2. brains.py   — hybrid backend: personas → local Nemotron, /ask → local
                   Claude Code CLI (read-only).
  3. personas.py — analyst voices loaded from analysts/*.md.
  4. bot.py      — the discord.py client wiring it together + a TPE scheduler.
"""

from __future__ import annotations

__all__ = ["config", "personas", "brains", "meetings"]
