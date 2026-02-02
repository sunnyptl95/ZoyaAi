# game.py
import time
import random
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
import social_db
import config

# --- 1. BALANCE CHECK (/bal) ---
async def check_balance(client, message):
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        # Force Register on check too (Optional but good)
        u = message.reply_to_message.from_user
        social_db.register_user_if_not_exists(u.id, u.first_name, u.username or "None")
    else:
        target_id = message.from_user.id
        
    name, balance, protect_until, steals = social_db.get_wallet(target_id)
    rank = social_db.get_rank(target_id)
    
    if protect_until > int(time.time()):
        time_left = int((protect_until - time.time()) / 3600)
        protect_status = f"🛡️ **Active** ({time_left}h left)"
    else:
        protect_status = "❌ **Not Protected**"

    text = (
        f"💳 **Bank of Zoya**\n\n"
        f"👤 **Name:** {name}\n"
        f"💰 **Balance:** ₹{balance}\n"
        f"🏆 **Global Rank:** #{rank}\n"
        f"🥷 **Successful Robberies:** {steals}\n"
        f"🛡️ **Security:** {protect_status}\n"
    )
    await message.reply_text(text)

# --- 2. ROB SYSTEM (/rob) ---
async def rob_user(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ **Kis ko lootna hai?**\nUse rob on reply message!")
        return
    
    robber_id = message.from_user.id
    victim = message.reply_to_message.from_user
    victim_id = victim.id
    
    if robber_id == victim_id:
        await message.reply_text("🙄 **Khud ko rob karega? Pagal hai kya?**")
        return

    if victim.is_bot:
         await message.reply_text("🤖 **Mujhe ya mere dosto ko rob karega? Himmat dekho!**")
         return

    # --- 1. FORCE REGISTER VICTIM (If New) ---
    social_db.register_user_if_not_exists(victim_id, victim.first_name, victim.username or "None")
    
    # --- 2. CHECK COOLDOWN ---
    can_rob, minutes_left = social_db.check_rob_cooldown(robber_id, victim_id)
    if not can_rob:
        await message.reply_text(f"⏳ **Cooldown Active!**\n you already robed. **{minutes_left} mins**")
        return

    # Fetch Wallets
    r_name, r_bal, r_prot, r_steals = social_db.get_wallet(robber_id)
    v_name, v_bal, v_prot, v_steals = social_db.get_wallet(victim_id)
    
    # 3. Check Protection
    if v_prot > int(time.time()):
        await message.reply_text(f"🛡️ **Failed!** {v_name} is Protected")
        return
    
    # 4. Check Minimum Balance
    if v_bal < 50:
        await message.reply_text(f"🥺 **Rehne de bhai, {v_name} pehle se gareeb hai.** (Balance < ₹50)")
        return
        
    # 5. Probability Calculation (Success 90%)
    success = random.randint(1, 100) <= 90 
    
    if success:
        percent = random.randint(30, 70)
        stolen_amount = int((v_bal * percent) / 100)
        
        social_db.update_balance(robber_id, stolen_amount)
        social_db.update_balance(victim_id, -stolen_amount)
        social_db.increment_steals(robber_id)
        
        # Set Cooldown
        social_db.add_rob_cooldown(robber_id, victim_id)
        
        await message.reply_text(
            f"🔫 **ROBBERY SUCCESS!**\n\n"
            f"😈 you rob from {v_name}!\n"
            f"💸 **Stolen:** ₹{stolen_amount}\n"
            f"💰 **Ur New Balance:** ₹{r_bal + stolen_amount}"
        )
    else:
        # Fail & Penalty
        fine = 50
        social_db.update_balance(robber_id, -fine)
        await message.reply_text(
            f"🚓 **POLICE CAUGHT YOU!**\n\n"
            f"😂 You fail,{v_name} call the polie!\n"
            f"💸 **Fine Paid:** ₹{fine}\n"
            f"🥺 **Try again later.**"
        )

# --- 3. PROTECTION SYSTEM (/protect) ---
async def buy_protection(client, message):
    try:
        if len(message.command) < 2:
            await message.reply_text("🛡️ **Security Plans:**\n\n`/protect 1d` - ₹150 (1 Day)\n`/protect 2d` - ₹300 (2 Days)\n(Aur reply me `/bal` check karo)")
            return
            
        days_str = message.command[1].lower().replace("d", "")
        days = int(days_str)
        
        if days < 1 or days > 2:
            await message.reply_text("⚠️ **Limit:** Max 2 days.")
            return
            
        cost = days * config.PROTECT_COST_PER_DAY
        user_id = message.from_user.id
        name, balance, current_prot, steals = social_db.get_wallet(user_id)
        
        if current_prot > int(time.time()):
            await message.reply_text("👮 **Already Protected!**.")
            return
            
        if balance < cost:
            await message.reply_text(f"❌ **Garib!** you have ₹{balance}, need ₹{cost}.")
            return
            
        expiry = social_db.set_protection(user_id, days, cost)
        await message.reply_text(f"✅ **Security Active!**\n🛡️ now you are safe for {days} days.\n💸 **Paid:** ₹{cost}")
        
    except ValueError:
        await message.reply_text("⚠️ Use format: `/protect 1d`")

# --- 4. LEADERBOARD (/top) ---
async def leaderboard(client, message):
    top_users = social_db.get_top_rich()
    if not top_users:
        await message.reply_text("📉 Abhi koi ameer nahi hai.")
        return
    text = "🏆 **Richest Users (Top 10)**\n\n"
    for i, (name, bal) in enumerate(top_users, 1):
        medal = "🥇" if i==1 else "🥈" if i==2 else "🥉" if i==3 else f"{i}."
        text += f"{medal} **{name}** — ₹{bal}\n"
    await message.reply_text(text)

# --- 5. TOP THIEVES (Owner Only) ---
async def show_top_thieves(client, message):
    if message.from_user.id != config.OWNER_ID:
        await message.reply_text("❌ only **Master**!")
        return

    top_thieves = social_db.get_top_thieves()
    if not top_thieves:
        await message.reply_text("🕊️ Abhi tak sab shareef hain (No Robberies).")
        return

    text = "🥷 **Most Wanted Thieves (Top 10)**\n\n"
    for i, (name, count) in enumerate(top_thieves, 1):
        text += f"{i}. **{name}** — {count} Robberies\n"
    
    await message.reply_text(text)

# --- EXPORT HANDLERS ---
rob_handler = MessageHandler(rob_user, filters.command("rob") & filters.group)
protect_handler = MessageHandler(buy_protection, filters.command("protect"))
bal_handler = MessageHandler(check_balance, filters.command(["bal", "balance"]))
top_handler = MessageHandler(leaderboard, filters.command(["top", "leaderboard"]))
thieves_handler = MessageHandler(show_top_thieves, filters.command("thieves"))

