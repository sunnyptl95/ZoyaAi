# ai.py
import os
import asyncio
import random
import json
import datetime
import time
from collections import deque
from pyrogram import Client, filters, enums
from pyrogram.handlers import MessageHandler
from groq import Groq
import config
import social_db

# --- 🔄 KEY ROTATION SETUP ---
current_key_index = 0

chat_memory = {}
enabled_chats = []

# --- 🔥 CROWD MODE VARIABLES ---
chat_heat = {}

# --- 🎮 MODES ---
auto_save_mode = False 

# --- MEMORY SETTINGS ---
MEMORY_LIMIT = 30

# --- STICKER LOADING SYSTEM ---
STICKER_DB_FILE = "stickers.txt"
loaded_stickers = []

def load_stickers_from_file():
    global loaded_stickers
    loaded_stickers = [] 
    
    # Config se load karo
    if "RANDOM" in config.STICKERS:
        loaded_stickers.extend(config.STICKERS["RANDOM"])
    
    # File se load karo
    if os.path.exists(STICKER_DB_FILE):
        try:
            with open(STICKER_DB_FILE, "r") as f:
                file_stickers = [line.strip() for line in f if line.strip()]
                loaded_stickers.extend(file_stickers)
        except: pass
    
    loaded_stickers = list(set(loaded_stickers))
    print(f"✅ AI Loaded: {len(loaded_stickers)} Stickers ready.")

def save_new_sticker(file_id):
    if file_id not in loaded_stickers:
        with open(STICKER_DB_FILE, "a") as f:
            f.write(f"{file_id}\n")
        loaded_stickers.append(file_id)
        return True
    return False

load_stickers_from_file()

# --- MEMORY FUNCTIONS ---
if os.path.exists(config.MEMORY_FILE):
    try:
        with open(config.MEMORY_FILE, "r") as f:
            data = json.load(f)
            for chat_id, msgs in data.items():
                chat_memory[int(chat_id)] = deque(msgs, maxlen=MEMORY_LIMIT)
    except Exception as e:
        print(f"Memory Load Error: {e}")

if os.path.exists(config.AI_ENABLED_FILE):
    try:
        with open(config.AI_ENABLED_FILE, "r") as f:
            enabled_chats = [int(line.strip()) for line in f if line.strip()]
    except: pass

def save_enabled_chats():
    with open(config.AI_ENABLED_FILE, "w") as f:
        for chat_id in enabled_chats:
            f.write(f"{chat_id}\n")

def save_memory_to_file():
    serializable_memory = {str(k): list(v) for k, v in chat_memory.items()}
    with open(config.MEMORY_FILE, "w") as f:
        json.dump(serializable_memory, f)

def get_random_sticker():
    if loaded_stickers: return random.choice(loaded_stickers)
    return None

# --- 🔥 HEAT CALCULATION (Crowd Logic) ---
def update_chat_heat(chat_id):
    """Checks how active the group is right now"""
    current_time = time.time()
    
    if chat_id not in chat_heat:
        chat_heat[chat_id] = {"count": 1, "last_time": current_time}
        return 1
    
    data = chat_heat[chat_id]
    
    if current_time - data["last_time"] > 120:
        data["count"] = 1
    else:
        data["count"] += 1
        
    data["last_time"] = current_time
    return data["count"]

# --- 🔥 MAIN LOGIC: AI REPLY ---
def get_ai_reply(chat_id, user_id, user_name, user_text):
    global current_key_index
    extra_context = ""
    
    # 1. Fetch User's Global History (Important Fix)
    try:
        user_past = social_db.fetch_user_history(user_id)
        if user_past:
            extra_context += user_past
    except Exception as e:
        print(f"History Error: {e}")

    # 2. Gossip Logic (Owner Only)
    if chat_id == config.OWNER_ID:
        triggers = ["kya hua", "kya chal raha", "update", "news", "delete"]
        if any(w in user_text.lower() for w in triggers):
            gossip_data = social_db.get_gossip_context()
            extra_context += (
                f"\n\n[SECRET MEMORY ACCESS]:\n{gossip_data}\n"
                f"[INSTRUCTION]: Gossip naturally about this."
            )

    # 3. Recognition Logic
    words = user_text.split()
    search_query = None
    for w in words:
        if w.startswith("@"): 
            search_query = w
            break
        elif w[0].isupper() and len(w) > 3 and w.lower() not in ["zoya", "kaise", "master", "nahi", "bhai"]:
            search_query = w
    
    if search_query:
        info = social_db.get_user_info(search_query)
        if info:
            extra_context += (
                f"\n\n[SOCIAL GRAPH MATCH]: You know '{info['name']}'. "
                f"Seen in '{info['last_group']}' {info['last_seen_ago']} mins ago."
            )

    # Initialize Memory
    if chat_id not in chat_memory:
        chat_memory[chat_id] = deque(maxlen=MEMORY_LIMIT)

    # Add Message to Context
    chat_memory[chat_id].append({"role": "user", "content": f"{user_name}: {user_text}"})

    now = datetime.datetime.now()
    date_time_str = now.strftime("%A, %d %B %Y, %I:%M %p")
    
    # System Prompt Injection
    system_prompt_with_time = f"{config.AI_SYSTEM_PROMPT}\n\n[Current Time: {date_time_str}]{extra_context}"
    
    messages_payload = [{"role": "system", "content": system_prompt_with_time}]
    messages_payload.extend(list(chat_memory[chat_id]))

    max_retries = len(config.GROQ_API_KEY)
    
    for attempt in range(max_retries):
        try:
            api_key = config.GROQ_API_KEY[current_key_index]
            temp_client = Groq(api_key=api_key)

            chat_completion = temp_client.chat.completions.create(
                messages=messages_payload,
                model=config.AI_MODEL,
                temperature=0.8,
                max_tokens=150
            )
            reply = chat_completion.choices[0].message.content
            
            chat_memory[chat_id].append({"role": "assistant", "content": reply})
            save_memory_to_file()
            return reply

        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                print(f"⚠️ Key Switch: {current_key_index}")
                current_key_index = (current_key_index + 1) % len(config.GROQ_API_KEY)
                time.sleep(1)
                continue 
            return None
    return None

# --- HANDLERS ---
async def set_save_mode(client, message):
    global auto_save_mode
    if message.from_user.id != config.OWNER_ID: return
    command = message.command[1].lower() if len(message.command) > 1 else "off"
    if command == "on":
        auto_save_mode = True
        await message.reply_text("📥 **Saving Mode ON**")
    else:
        auto_save_mode = False
        await message.reply_text("🎮 **Gaming Mode ON**")

async def toggle_chat(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # --- Admin Check Logic ---
    is_authorized = False
    
    # 1. Check if user is the Master (Owner)
    if user_id == config.OWNER_ID:
        is_authorized = True
    else:
        # 2. Check if the USER is an admin in the group
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                is_authorized = True
        except Exception:
            is_authorized = False

    if not is_authorized:
        await message.reply_text("❌ Sirf group ke **Admins** hi ye kar sakte hain! 😤")
        return

    # --- Toggle Action ---
    if len(message.command) > 1:
        action = message.command[1].lower()
        if action == "on":
            if chat_id not in enabled_chats:
                enabled_chats.append(chat_id)
                save_enabled_chats()
                await message.reply_text("Now I am Online ! ❤️")
            else:
                await message.reply_text("Open Your Eyes , I am already on 🙄")
        
        elif action == "off":
            if chat_id in enabled_chats:
                enabled_chats.remove(chat_id)
                save_enabled_chats()
                await message.reply_text("Bye! chat mode off. 😒")
            else:
                await message.reply_text("Me already off. 🤷‍♀️")
    else:
        await message.reply_text("Usage: `/chat on` or `/chat off`")


async def handle_incoming_sticker(client, message):
    chat_id = message.chat.id
    is_private = message.chat.type == enums.ChatType.PRIVATE
    
    # Save Logic
    if is_private and message.from_user.id == config.OWNER_ID and auto_save_mode:
        if message.sticker and save_new_sticker(message.sticker.file_id):
            await message.reply_text(f"✅ Saved!")
            return 
            
    # Random Reply Logic
    if random.random() < 0.05:
        await asyncio.sleep(random.randint(1, 3))
        sticker_id = get_random_sticker()
        if sticker_id:
            try: await message.reply_sticker(sticker_id)
            except: pass

# --- ai_chat_handler logic ---
async def ai_chat_handler(client, message):
    chat_id = message.chat.id
    user_text = message.text
    if not user_text or user_text.startswith("/"): return

    user_name = "Master" if message.from_user.id == config.OWNER_ID else message.from_user.first_name
    user_id = message.from_user.id
    is_private = message.chat.type == enums.ChatType.PRIVATE
    
    try:
        is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == (await client.get_me()).id
    except: is_reply_to_bot = False

    # 🔥 NEW PROBABILITY LOGIC:
    msg_density = update_chat_heat(chat_id)
    reply_probability = 0.02
    if msg_density > 10: reply_probability = 0.10
    
    should_reply = False
    if is_private:
        should_reply = True
    else:
        if chat_id in enabled_chats:
            if is_reply_to_bot or "zoya" in user_text.lower() or message.mentioned:
                should_reply = True
            elif random.random() < reply_probability:
                should_reply = True
            
    if not should_reply: return

    try: await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
    except: pass 

    await asyncio.sleep(random.uniform(1, 2.5)) # Natural delay
    response = get_ai_reply(chat_id, user_id, user_name, user_text)
    
    if response:
        # CLEAN ALL TAGS
        clean_response = response.replace("[STICKER_LOVE]", "").replace("[STICKER_ANGRY]", "").replace("[STICKER_FUNNY]", "").replace("[STICKER_SAD]", "").strip()
        
        if clean_response:
            try: await message.reply_text(clean_response)
            except: pass
            
        # Sticker chance reduced to 30% for less spam
        if random.random() < 0.30:
            sticker_to_send = get_random_sticker()
            if sticker_to_send:
                try: 
                    await asyncio.sleep(0.5)
                    await client.send_sticker(chat_id, sticker_to_send)
                except: pass

# --- EXPORT HANDLERS ---
save_mode_handler = MessageHandler(set_save_mode, filters.command("save") & filters.private)
chat_toggle_handler = MessageHandler(toggle_chat, filters.command("chat") & filters.group)
ai_sticker_handler = MessageHandler(handle_incoming_sticker, (filters.sticker | filters.animation) & (~filters.bot))
ai_text_handler = MessageHandler(ai_chat_handler, filters.text & (~filters.bot))

