# tag.py (Fixed & Debugged)
import asyncio
import random
import os
import time
from pyrogram import Client, filters, enums
from pyrogram.handlers import MessageHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChatAdminRequired, FloodWait
import config 

tagging_status = {}

# --- HELPER FUNCTIONS ---
def add_chat(chat_id):
    if not os.path.exists(config.USERS_DB_FILE):
        with open(config.USERS_DB_FILE, "w") as f: f.write("")
    with open(config.USERS_DB_FILE, "r") as f:
        users = f.read().splitlines()
    if str(chat_id) not in users:
        with open(config.USERS_DB_FILE, "a") as f:
            f.write(f"{chat_id}\n")

def save_voice(chat_id, message_id):
    with open(config.VOICE_DB_FILE, "a") as f:
        f.write(f"{chat_id}:{message_id}\n")

def get_all_voices():
    if not os.path.exists(config.VOICE_DB_FILE): return []
    voices = []
    with open(config.VOICE_DB_FILE, "r") as f:
        for line in f:
            if ":" in line:
                parts = line.strip().split(":")
                voices.append({"chat_id": int(parts[0]), "message_id": int(parts[1])})
    return voices

def add_to_delete_queue(chat_id, message_id):
    expiry_time = int(time.time()) + config.DELETE_TIME
    with open(config.DELETE_QUEUE_FILE, "a") as f:
        f.write(f"{chat_id}:{message_id}:{expiry_time}\n")

async def run_startup_cleanup(client):
    if not os.path.exists(config.DELETE_QUEUE_FILE): return
    new_lines = []
    current_time = int(time.time())
    with open(config.DELETE_QUEUE_FILE, "r") as f:
        lines = f.readlines()
    for line in lines:
        try:
            parts = line.strip().split(":")
            chat_id, msg_id, expiry = int(parts[0]), int(parts[1]), int(parts[2])
            if current_time >= expiry:
                try: await client.delete_messages(chat_id, msg_id)
                except: pass 
            else:
                new_lines.append(line)
                asyncio.create_task(delayed_delete(client, chat_id, msg_id, expiry - current_time))
        except: continue
    with open(config.DELETE_QUEUE_FILE, "w") as f:
        f.writelines(new_lines)

async def delayed_delete(client, chat_id, message_id, delay):
    await asyncio.sleep(delay)
    try: await client.delete_messages(chat_id, message_id)
    except: pass

# --- HANDLERS ---
async def start_command(client, message):
    add_chat(message.chat.id)
    if message.chat.type == enums.ChatType.PRIVATE:
        text = (
            "👋 **Welcome to Zoya + Game Bot!**\n\n"
            "**🤖 AI Commands:**\n"
            "• `/chat on` - Enable AI\n"
            "• `/chat off` - Disable AI\n\n"
            "**💰 Economy Game:**\n"
            "• `/rob` - Steal Money (Reply user)\n"
            "• `/protect` - Buy Security (1d/2d)\n"
            "• `/bal` - Check Bank & Rank\n"
            "• `/top` - Rich List\n\n"
            "**🏷️ Tag Commands:**\n"
            "• `/voicetag` - Tag with Voice\n"
            "• `/tagall` - Tag with Text\n"
            "• `/stoptag` - Stop\n\n"
            "⚠️ **Note:** Make me **ADMIN**, To better Experience!\n• In Dm You can chat without any command just Say Hii or hello."
        )
        # Indentation fixed to use spaces only
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Me to Group", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")],
            [InlineKeyboardButton("📢 Updates", url="https://t.me/THINKOF5"), InlineKeyboardButton("🎧 Support", url="https://t.me/redvinus")]
        ])
        await message.reply_text(text, reply_markup=buttons)
    else:
        await message.reply_text("✅ Zoya is Online! /bal to check money.")

async def save_voice_handler_func(client, message):
    if message.from_user.id != config.OWNER_ID: return
    save_voice(message.chat.id, message.id)
    await message.reply_text(f"✅ Voice Saved! Total: {len(get_all_voices())}")

async def voice_tag(client, message):
    chat_id = message.chat.id
    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            await message.reply_text("❌ Only Admins!")
            return
        admin_mention = message.from_user.mention
    except: return

    voices = get_all_voices()
    if not voices:
        await message.reply_text("❌ Database Empty! Tell Master to add.")
        return

    await message.reply_text(f"🚀 **Voice Tagging Started by {admin_mention}!**")
    tagging_status[chat_id] = True
    
    batch = []
    total_tagged = 0
    members_found = False

    try:
        async for member in client.get_chat_members(chat_id):
            if not tagging_status.get(chat_id, False): break
            
            if not member.user.is_bot and not member.user.is_deleted:
                members_found = True
                batch.append(member.user.mention)
            
            if len(batch) == 5:
                voice = random.choice(voices)
                try:
                    sent = await client.copy_message(chat_id, voice["chat_id"], voice["message_id"], caption=" ".join(batch))
                    total_tagged += 5
                    if sent:
                        add_to_delete_queue(chat_id, sent.id)
                        asyncio.create_task(delayed_delete(client, chat_id, sent.id, config.DELETE_TIME))
                    await asyncio.sleep(2)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except: pass
                batch = []

        # --- IMPORTANT: LEFTOVER BATCH ---
        if batch and tagging_status.get(chat_id, False):
            voice = random.choice(voices)
            try:
                sent = await client.copy_message(chat_id, voice["chat_id"], voice["message_id"], caption=" ".join(batch))
                total_tagged += len(batch)
                if sent:
                    add_to_delete_queue(chat_id, sent.id)
                    asyncio.create_task(delayed_delete(client, chat_id, sent.id, config.DELETE_TIME))
            except: pass
    
    except ChatAdminRequired:
        await message.reply_text("❌ **Error:** make me admin (with 'Ban Users')!")
        return
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
        return

    tagging_status[chat_id] = False
    
    if not members_found:
        await message.reply_text("❌ **Error:** 0 Members found! Please Privacy Mode off and Permissions check.")
    else:
        await message.reply_text(f"✅ **Tagging Complete!** Total {total_tagged} members tagged.")

async def tag_all(client, message):
    chat_id = message.chat.id
    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            await message.reply_text("❌ Only admins!")
            return
    except: return

    custom_msg = "📢 Attention!"
    if len(message.command) > 1: custom_msg = message.text.split(None, 1)[1]

    tagging_status[chat_id] = True
    await message.reply_text("✅ **Text Tagging Started!**")
    
    batch = []
    total_tagged = 0
    members_found = False

    try:
        async for member in client.get_chat_members(chat_id):
            if not tagging_status.get(chat_id, False): break
            
            if not member.user.is_bot and not member.user.is_deleted:
                members_found = True
                batch.append(member.user.mention)
            
            if len(batch) == 5:
                try:
                    await client.send_message(chat_id, f"{custom_msg}\n\n{' '.join(batch)}")
                    total_tagged += 5
                    await asyncio.sleep(2)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except: pass
                batch = []
        
        # --- IMPORTANT: LEFTOVER BATCH ---
        if batch and tagging_status.get(chat_id, False):
            try:
                await client.send_message(chat_id, f"{custom_msg}\n\n{' '.join(batch)}")
                total_tagged += len(batch)
            except: pass

    except ChatAdminRequired:
        await message.reply_text("❌ **Error:** Make me admin (with 'Ban Users' permission)!")
        return
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
        return
    
    tagging_status[chat_id] = False

    if not members_found:
        await message.reply_text("❌ **Error:** 0 Members found ! maybe permissions error.")
    else:
        await message.reply_text(f"✅ **Tagging Done.** Total {total_tagged} tagged.")

async def stop_tag(client, message):
    tagging_status[message.chat.id] = False
    await message.reply_text("🛑 **Tagging Stopped.**")

async def broadcast(client, message):
    if message.from_user.id != config.OWNER_ID: return 
    if not message.reply_to_message: return
    status = await message.reply_text("⚡ Broadcasting...")
    
    count = 0
    if os.path.exists(config.USERS_DB_FILE):
        with open(config.USERS_DB_FILE, "r") as f:
            chats = [int(line.strip()) for line in f if line.strip()]
        for chat_id in chats:
            try:
                await client.copy_message(chat_id, message.chat.id, message.reply_to_message.id)
                count += 1
                await asyncio.sleep(0.3) 
            except: pass
    await status.edit(f"✅ Broadcast Sent to {count} chats.")

# --- EXPORT HANDLERS ---
start_handler = MessageHandler(start_command, filters.command("start"))
voice_saver_handler = MessageHandler(save_voice_handler_func, (filters.voice | filters.audio) & filters.private)
tag_all_handler = MessageHandler(tag_all, filters.command("tagall") & filters.group)
voice_tag_handler = MessageHandler(voice_tag, filters.command("voicetag") & filters.group)
stop_tag_handler = MessageHandler(stop_tag, filters.command("stoptag") & filters.group)
broadcast_handler = MessageHandler(broadcast, filters.command("broadcast") & filters.user(config.OWNER_ID))

