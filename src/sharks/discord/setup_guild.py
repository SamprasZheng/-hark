"""One-shot: create the 精簡版 channel layout, then print the privacy checklist.

Run once after the bot has joined the server:

    python -m sharks.discord.setup_guild

What it DOES (content only): creates a `PolkaSharks` category and the eight
minimal text channels (and optional voice channels) if they don't already exist,
then posts a pinned-worthy welcome to #bot-狀態.

What it deliberately does NOT do: it never changes server security / access
controls (invites, verification level, Community/Discoverable, roles). Those are
sensitive and stay a human action — the script prints an exact checklist instead.
The bot never adds members.
"""

from __future__ import annotations

import discord

from sharks.discord import config as C
from sharks.discord.config import Settings

WELCOME = (
    "**PolkaSharks 私人投研伺服器** 🦈\n"
    "- **#晨會 / #晚會** — 每日自動開會(07:30 / 22:30 TPE):盤勢姿態、台美股行情、選股。\n"
    "- **#市場** — 總經 / 國際局勢 / 台美股討論。\n"
    "- **#每日選股** — 最近的 FOM 選股與每日訊號(只建議,不下單)。\n"
    "- **#問claude** — 直接打字問本地 Claude Code,唯讀讀得到整個 $hark。或用 `/ask`。\n"
    "- **#分析師議會** — 跟人格聊天:打 `huang: 你的問題` 或用 `/persona`。\n"
    "- **#雜談** — 隨意聊。\n"
    "- **#bot-狀態** — 上線狀態、排程、異常告警。\n\n"
    "指令:`/ask` `/persona` `/personas` `/picks` `/meeting` `/status`\n"
    "界線:本系統只做研究與建議,**永不代為下單/轉帳**;內容非個人化投資建議。"
)

PRIVACY_CHECKLIST = """
─────────────────────────────────────────────────────────────
🔒 私密鎖定清單(只有你和女友兩人 — 這些是 Discord 設定,bot 不會自動改)
─────────────────────────────────────────────────────────────
1. 伺服器設定 → 邀請(Invites):撤銷/刪除所有現有邀請連結。
2. 之後要邀人時:建立「24 小時、限用 1 次」的連結,用完即失效。
3. 伺服器設定 → 啟用社群(Enable Community):保持「關閉」(不要公開/可被搜尋)。
4. 伺服器設定 → 安全設定(Safety Setup)→ 驗證等級:設為「中」以上。
5. 角色 @everyone 權限:關掉「建立邀請」「管理…」等;一般成員只留發訊息/讀訊息。
6. 確認成員清單只有 你、你女友、以及這個 bot — 其餘一律移除。
7. bot 角色權限只需要:檢視頻道、發送訊息、嵌入連結、讀取歷史、管理 Webhook、
   管理頻道(建頻道用);不需要、也不要給「管理員(Administrator)」。
─────────────────────────────────────────────────────────────
"""


async def _build(client: discord.Client, settings: Settings) -> None:
    guild = (client.get_guild(settings.guild_id) if settings.guild_id
             else (client.guilds[0] if client.guilds else None))
    if not guild:
        print("⚠️ bot 不在任何伺服器內 — 先用邀請連結把 bot 加進 PolkaSharks。")
        return
    print(f"伺服器:{guild.name} ({guild.id})")

    cat = discord.utils.get(guild.categories, name=C.MINIMAL_CATEGORY)
    if cat is None:
        cat = await guild.create_category(C.MINIMAL_CATEGORY)
        print(f"  + 類別 {C.MINIMAL_CATEGORY}")

    for name in C.MINIMAL_CHANNELS:
        if discord.utils.get(guild.text_channels, name=name) is None:
            await guild.create_text_channel(name, category=cat)
            print(f"  + 文字頻道 #{name}")
        else:
            print(f"  = #{name} 已存在")

    if settings.enable_voice:
        for name in C.VOICE_CHANNELS:
            if discord.utils.get(guild.voice_channels, name=name) is None:
                await guild.create_voice_channel(name, category=cat)
                print(f"  + 語音頻道 🔊{name}")

    status = discord.utils.get(guild.text_channels, name=C.CH_STATUS)
    if status:
        await status.send(WELCOME)
    print("✅ 頻道建立完成。")
    print(PRIVACY_CHECKLIST)


def main() -> int:
    settings = Settings.load()
    if not settings.token:
        print("DISCORD_BOT_TOKEN 為空 — 先建立 bot 並把 token 放進 $hark/.env")
        return 1
    intents = discord.Intents.default()
    intents.members = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:  # pragma: no cover - network
        try:
            await _build(client, settings)
        finally:
            await client.close()

    client.run(settings.token, log_handler=None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
