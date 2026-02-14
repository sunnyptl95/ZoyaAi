# 🤖 Zoya - Advanced AI & Economy Telegram Bot Template

This is an open-source Telegram Bot template that combines **Artificial Intelligence (Groq/Llama)** with a fun **Economy Game** system. 

It is designed to be easily customizable. You can change the AI's personality, modify the game rules, and host it yourself.

## ✨ Features
- **🧠 Human-like AI:** Powered by Groq (Llama 3.3). It remembers conversation history and context.
- **🤬 Personality Mode:** Comes with a built-in "Zoya" personality (Savage/Funny), but you can change it to anything.
- **💰 Economy System:** Bank, Robbery, Protection shields, and Leaderboards.
- **🛡️ Group Tools:** Tag all members, Voice tagging, Welcome messages.
- **🧠 Memory:** Remembers users across different groups.

## 🚀 Installation Guide

### Install Requirements
  -  Make sure you have Python 3.9+ installed.

Bash
  pip install -r requirements.txt


### ⚙️ 3. `config.py` (Clean Version)
# config.py - Configuration File

# Get these from https://my.telegram.org
API_ID = 12345678  # Enter your API ID (Integer)
API_HASH = "YOUR_API_HASH_HERE"

# Get this from @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Get these from https://console.groq.com/keys
# You can add multiple keys for rotation
GROQ_API_KEY = [
    "gsk_key1_here",
    "gsk_key2_here"
]

# Your Telegram User ID (To control the bot)
OWNER_ID = 123456789
SUDO_USERS = [123456789]

# --- 🤖 AI Character Settings ---
AI_MODEL = "llama-3.3-70b-versatile"

# CUSTOMIZE YOUR BOT PERSONALITY HERE
AI_SYSTEM_PROMPT = (
    "You are Zoya, a virtual assistant. "
    "Personality: Helpful, Witty, and slightly savage. "
    "Rules: Keep answers short (under 20 words). "
    "Language: Hinglish (Hindi + English)."
)

# --- 📂 File Paths ---
AI_ENABLED_FILE = "ai_enabled_groups.txt"
USERS_DB_FILE = "users_db.txt"
VOICE_DB_FILE = "voice_db.txt"
DELETE_QUEUE_FILE = "pending_delete.txt"
MEMORY_FILE = "zoya_memory.json"

# --- ⚙️ Other Settings ---
DELETE_TIME = 18000  # 5 Hours

# Add Sticker File IDs here
STICKERS = {
    "RANDOM": [
        "CAACAgUAAxkBAAEQXO9pekOrKYN8W3nSq6CV4vfXXSPVvAACOhYAAp91AAFUqrX-c6LGI1A4BA",
    ]
}

# --- 💰 Economy Settings ---
START_BALANCE = 130
PROTECT_COST_PER_DAY = 150
CHAT_REWARD_MIN = 3
CHAT_REWARD_MAX = 11

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/Zoya-AI-Bot.git](https://github.com/YOUR_USERNAME/Zoya-AI-Bot.git)
cd Zoya-AI-Bot 

