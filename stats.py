# stats.py
from pyrogram import Client, filters, enums
from pyrogram.handlers import MessageHandler
import social_db
import config
import asyncio

# --- 1. PUBLIC STATS COMMAND ---
async def show_stats(client, message):
    # Database se count nikalo
    users, groups = social_db.get_stats()
    
    # Animation effect (Optional: Real feel ke liye)
    msg = await message.reply_text("🔄 **Checking Database...**")
    await asyncio.sleep(1)
    
    text = (
        f"📊 **Zoya's Network Stats**\n\n"
        f"👥 **Users Known:** {users}\n"
        f"🏘️ **Groups Active:** {groups}\n\n"
        f"⚡ *Powered by Real Human Memory™* 😉"
    )
    await msg.edit(text)

# --- 2. GROUP LIST (Owner Only) ---
async def show_group_list(client, message):
    if message.from_user.id != config.OWNER_ID:
        await message.reply_text("❌ Only **Master** ")
        return

    msg = await message.reply_text("📂 Fetching Group List...")
    text = social_db.get_group_list_formatted()
    
    if len(text) > 4000:
        with open("groups.txt", "w", encoding="utf-8") as f:
            f.write(text)
        await message.reply_document("groups.txt", caption="📂 Here is list.")
        await msg.delete()
    else:
        await msg.edit(text)

# --- 3. USER LIST (Owner Only) ---
async def show_user_list(client, message):
    if message.from_user.id != config.OWNER_ID:
        await message.reply_text("❌ Only for **Master** ! 🤫")
        return

    msg = await message.reply_text("👥 Fetching User List...")
    text = social_db.get_user_list_formatted()
    
    if len(text) > 4000:
        with open("users.txt", "w", encoding="utf-8") as f:
            f.write(text)
        await message.reply_document("users.txt", caption="👥 here is my friends (Users).")
        await msg.delete()
    else:
        await msg.edit(text)

# --- HANDLERS EXPORT ---
stats_handler = MessageHandler(show_stats, filters.command("stats"))
glist_handler = MessageHandler(show_group_list, filters.command("glist"))
ulist_handler = MessageHandler(show_user_list, filters.command("ulist"))