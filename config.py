# config.py
import os

API_ID = 12345578
API_HASH = ""
BOT_TOKEN = ""

#add multiple groq api keys for rotation , you can add one but it's limited suggest add multiple 
GROQ_API_KEY = ["",
	""]

# --- 👤 Admin & Owner ---
OWNER_ID = 7824703343
SUDO_USERS = [7824703343]

# --- 🤖 AI Character Settings ---
AI_MODEL = "llama-3.3-70b-versatile"

AI_SYSTEM_PROMPT = ( # give promte ex :
    "You are a 20-year-old Indian girl. You are NOT an AI. Personality: Muh-fat (straightforward), Ziddi, Flirty par moody."
)

# --- 📂 Files ---
AI_ENABLED_FILE = "ai_enabled_groups.txt"
USERS_DB_FILE = "users_db.txt"
VOICE_DB_FILE = "voice_db.txt"
DELETE_QUEUE_FILE = "pending_delete.txt"
MEMORY_FILE = "zoya_memory.json"
# --- ⚙️ Other Settings ---
DELETE_TIME = 18000  # 5 Hours

STICKERS = {
    "RANDOM": [
        "CAACAgUAAxkBAAEQXO9pekOrKYN8W3nSq6CV4vfXXSPVvAACOhYAAp91AAFUqrX-c6LGI1A4BA",
        "CAACAgUAAxkBAAEQXPNpekPtqf_fHqIyfcHRi4v2lbFu1gACXQcAAlDBgVRUQV2GTwZdWjgE",
        "CAACAgIAAxkBAAEQXPdpekQWNj2jLkuyKUldG25nKwkrYAACO3wAAhavIUvI-skp8D3UIjgE",
        "CAACAgIAAxkBAAEQXPlpekQv_ybDBAVD56YF9HDpAwABObEAAs-SAAK0ZMBLWQABb1A2oAN1OAQ",
        "CAACAgIAAxkBAAEQXQppekVOTS_MMvA3rUmrhBsTs6WYZgACyTwAAhlbCUuh0Yi9fQABawI4BA",
        "CAACAgUAAxkBAAEQXQhpekVLJgbEYwyGFOI8eq2iQWNCygACXAQAAp1xoFVl5P44191gizgE",
        "CAACAgUAAxkBAAEQXQZpekVI87NgGRROOXEmMu7wPmCSuwACxQQAAiPkcD3ODU0I1PirbDgE",
        "CAACAgUAAxkBAAEQXQJpekVE8eIeMexSfLxmmwGIRmU2WQACjAMAAjYkaVUtSwS1pp6VnDgE",
        "CAACAgUAAxkBAAEQXQABaXpFQ5yjXwgEZwy4mUETzzFtXRQAAl8EAAKtSKhUnRcMPf9Nc8U4BA"
    ]
}

# --- 💰 Economy Settings ---
START_BALANCE = 130
PROTECT_COST_PER_DAY = 150
CHAT_REWARD_MIN = 3
CHAT_REWARD_MAX = 11

