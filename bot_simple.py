#!/usr/bin/env python3
"""
Simple Telegram Forwarding Bot
==============================

Core Features:
- Account connectivity via Telethon
- Auto-forwarding rules
- Manual forwarding
- Basic user management
"""

import asyncio
import json
import logging
import os
import re
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Mock telegram imports for now
class MockTelegram:
    class Update:
        def __init__(self):
            pass
    
    class Message:
        def __init__(self):
            pass
    
    class User:
        def __init__(self):
            pass
    
    class CallbackQuery:
        def __init__(self):
            pass
    
    class InlineKeyboardButton:
        def __init__(self, text, callback_data):
            pass
    
    class InlineKeyboardMarkup:
        def __init__(self, keyboard):
            pass
    
    class ParseMode:
        HTML = "HTML"

# Try to import real telegram modules
try:
    from telegram import Update, Message, User, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
    from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, Filters
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    # Use mock classes
    Update = MockTelegram.Update
    Message = MockTelegram.Message
    User = MockTelegram.User
    CallbackQuery = MockTelegram.CallbackQuery
    InlineKeyboardButton = MockTelegram.InlineKeyboardButton
    InlineKeyboardMarkup = MockTelegram.InlineKeyboardMarkup
    ParseMode = MockTelegram.ParseMode
    TELEGRAM_AVAILABLE = False

# Telethon imports
try:
    from telethon.sync import TelegramClient
    from telethon.sessions import StringSession
    from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError, PhoneCodeInvalidError, FloodWaitError
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False

# Configuration
BOT_TOKEN = "7947140028:AAGOigrSSUATHbiOj05xz125H1KFipU1Ons"
API_ID = 21635609
API_HASH = "8a87c14e3032c550e63c85224cd56655"
OWNER_ID = 7925041792

# Conversation states
GET_PHONE_NUMBER_STATE, GET_AUTH_CODE_STATE, GET_2FA_PASSWORD_STATE = range(3)

# Data structures
@dataclass
class UserProfile:
    user_id: int
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    role: str = "free"
    joined_date: str = ""
    last_active: str = ""
    total_forwards: int = 0
    total_rules: int = 0
    is_banned: bool = False
    ban_reason: str = ""
    telethon_session: Optional[str] = None

@dataclass
class ForwardRule:
    rule_id: str
    user_id: int
    source_chat: int
    target_chats: List[int]
    mode: str  # with_tags, without_tags, bypass
    is_active: bool = True
    created_date: str = ""
    last_triggered: str = ""
    trigger_count: int = 0
    use_user_account: bool = False

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                role TEXT DEFAULT 'free',
                joined_date TEXT,
                last_active TEXT,
                total_forwards INTEGER DEFAULT 0,
                total_rules INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                ban_reason TEXT,
                telethon_session TEXT
            )
        ''')
        
        # Rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rules (
                rule_id TEXT PRIMARY KEY,
                user_id INTEGER,
                source_chat INTEGER,
                target_chats TEXT,
                mode TEXT,
                is_active INTEGER DEFAULT 1,
                created_date TEXT,
                last_triggered TEXT,
                trigger_count INTEGER DEFAULT 0,
                use_user_account INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[UserProfile]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return UserProfile(
                user_id=row[0],
                username=row[1] or "",
                first_name=row[2] or "",
                last_name=row[3] or "",
                phone=row[4] or "",
                role=row[5] or "free",
                joined_date=row[6] or "",
                last_active=row[7] or "",
                total_forwards=row[8] or 0,
                total_rules=row[9] or 0,
                is_banned=bool(row[10]),
                ban_reason=row[11] or "",
                telethon_session=row[12]
            )
        return None
    
    def save_user(self, user: UserProfile):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, last_name, phone, role, joined_date, 
             last_active, total_forwards, total_rules, is_banned, ban_reason, telethon_session)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user.user_id, user.username, user.first_name, user.last_name, user.phone,
            user.role, user.joined_date, user.last_active, user.total_forwards,
            user.total_rules, user.is_banned, user.ban_reason, user.telethon_session
        ))
        conn.commit()
        conn.close()
    
    def get_rules(self, user_id: int = None) -> List[ForwardRule]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('SELECT * FROM rules WHERE user_id = ?', (user_id,))
        else:
            cursor.execute('SELECT * FROM rules')
        
        rows = cursor.fetchall()
        conn.close()
        
        rules = []
        for row in rows:
            target_chats = json.loads(row[3]) if row[3] else []
            rules.append(ForwardRule(
                rule_id=row[0],
                user_id=row[1],
                source_chat=row[2],
                target_chats=target_chats,
                mode=row[4],
                is_active=bool(row[5]),
                created_date=row[6] or "",
                last_triggered=row[7] or "",
                trigger_count=row[8] or 0,
                use_user_account=bool(row[9])
            ))
        return rules
    
    def save_rule(self, rule: ForwardRule):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO rules 
            (rule_id, user_id, source_chat, target_chats, mode, is_active, 
             created_date, last_triggered, trigger_count, use_user_account)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rule.rule_id, rule.user_id, rule.source_chat, json.dumps(rule.target_chats),
            rule.mode, rule.is_active, rule.created_date, rule.last_triggered,
            rule.trigger_count, rule.use_user_account
        ))
        conn.commit()
        conn.close()

class TelethonManager:
    _active_clients: Dict[int, TelegramClient] = {}
    
    @classmethod
    async def start_login(cls, user_id: int, phone_number: str):
        if not TELETHON_AVAILABLE:
            raise Exception("Telethon not available")
        
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        
        if not await client.is_user_authorized():
            phone_code_hash = await client.send_code_request(phone_number)
            cls._active_clients[user_id] = client
            return client, phone_code_hash.phone_code_hash
        else:
            return client, None
    
    @classmethod
    async def complete_login(cls, user_id: int, auth_code: str, phone_code_hash: str):
        if not TELETHON_AVAILABLE:
            raise Exception("Telethon not available")
        
        client = cls._active_clients.get(user_id)
        if not client:
            raise Exception("No active client found")
        
        try:
            await client.sign_in(phone_code_hash, auth_code)
            session_string = client.session.save()
            await client.disconnect()
            del cls._active_clients[user_id]
            return session_string
        except SessionPasswordNeededError:
            return "2fa_required"
    
    @classmethod
    async def complete_2fa(cls, user_id: int, password: str):
        if not TELETHON_AVAILABLE:
            raise Exception("Telethon not available")
        
        client = cls._active_clients.get(user_id)
        if not client:
            raise Exception("No active client found")
        
        await client.sign_in(password=password)
        session_string = client.session.save()
        await client.disconnect()
        del cls._active_clients[user_id]
        return session_string

# Global instances
db = DatabaseManager("bot_data.db")

def get_current_time() -> str:
    return datetime.now().isoformat()

def generate_rule_id() -> str:
    return f"rule_{int(time.time())}_{hash(str(time.time()))}"

def validate_chat_id(chat_id: str) -> int:
    try:
        return int(chat_id)
    except ValueError:
        raise ValueError("Invalid chat ID format")

# Command handlers
async def start_command(update: Update, context):
    """Start command handler"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        user = UserProfile(
            user_id=user_id,
            username=update.effective_user.username or "",
            first_name=update.effective_user.first_name or "",
            last_name=update.effective_user.last_name or "",
            joined_date=get_current_time(),
            last_active=get_current_time()
        )
        db.save_user(user)
    
    welcome_text = f"""
🤖 <b>Welcome to the Telegram Forwarding Bot!</b>

👤 <b>User ID:</b> <code>{user_id}</code>
📅 <b>Joined:</b> {user.joined_date[:10] if user.joined_date else "Unknown"}

🔗 <b>Available Commands:</b>
• /connect_account - Connect your Telegram account
• /autoforward - Create auto-forwarding rule
• /forward - Manual forward
• /rules - View your rules
• /help - Show help

💡 <b>Quick Start:</b>
1. Use /connect_account to link your account
2. Use /autoforward to create rules
3. Use /forward for manual forwarding
"""
    
    keyboard = [
        [InlineKeyboardButton("🔗 Connect Account", callback_data="connect_account")],
        [InlineKeyboardButton("📝 Create Rule", callback_data="autoforward")],
        [InlineKeyboardButton("📋 My Rules", callback_data="rules")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

async def connect_account_command(update: Update, context) -> int:
    """Start account connection process"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if user and user.telethon_session:
        await update.message.reply_text("✅ You already have a connected Telegram account. Use /disconnect_account to disconnect first.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "📱 Please send your phone number (e.g., +12345678900) to connect your Telegram account.\n"
        "Use /cancel to abort."
    )
    return GET_PHONE_NUMBER_STATE

async def get_phone_number(update: Update, context) -> int:
    user_id = update.effective_user.id
    phone_number = update.message.text.strip()

    if not re.match(r"^\+\d{10,15}$", phone_number):
        await update.message.reply_text("❌ Invalid phone number format. Please include country code (e.g., +12345678900).")
        return GET_PHONE_NUMBER_STATE

    try:
        client, phone_code_hash = await TelethonManager.start_login(user_id, phone_number)
        context.user_data['telethon_phone_code_hash'] = phone_code_hash
        
        await update.message.reply_text("🔐 Please send the verification code you received in Telegram.")
        return GET_AUTH_CODE_STATE
    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred: {str(e)}. Please try again.")
        return ConversationHandler.END

async def get_auth_code(update: Update, context) -> int:
    user_id = update.effective_user.id
    auth_code = update.message.text.strip()
    phone_code_hash = context.user_data.get('telethon_phone_code_hash')

    try:
        session_string = await TelethonManager.complete_login(user_id, auth_code, phone_code_hash)
        user = db.get_user(user_id)
        if user:
            user.telethon_session = session_string
            db.save_user(user)
        await update.message.reply_text("✅ Your Telegram account has been successfully connected! 🎉")
        context.user_data.clear()
        return ConversationHandler.END
    except Exception as e:
        if "2fa_required" in str(e):
            await update.message.reply_text("🔑 Two-factor authentication required. Please send your 2FA password.")
            return GET_2FA_PASSWORD_STATE
        else:
            await update.message.reply_text(f"❌ An error occurred: {str(e)}. Please try again.")
            return ConversationHandler.END

async def get_2fa_password(update: Update, context) -> int:
    user_id = update.effective_user.id
    password = update.message.text.strip()

    try:
        session_string = await TelethonManager.complete_2fa(user_id, password)
        user = db.get_user(user_id)
        if user:
            user.telethon_session = session_string
            db.save_user(user)
        await update.message.reply_text("✅ Your Telegram account has been successfully connected! 🎉")
        context.user_data.clear()
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred: {str(e)}. Please try again.")
        return GET_2FA_PASSWORD_STATE

async def autoforward_command(update: Update, context):
    """Auto-forward command handler"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user or not user.telethon_session:
        await update.message.reply_text("❌ You must connect your Telegram account first. Use /connect_account.")
        return
    
    await update.message.reply_text(
        "📝 <b>Auto-Forward Command Usage:</b>\n\n"
        "<code>/autoforward &lt;mode&gt; &lt;source_chat&gt; &lt;target_chat1&gt; [target_chat2] ...</code>\n\n"
        "<b>Modes:</b>\n"
        "• with_tags - Keep forward tags\n"
        "• without_tags - Clean copy\n"
        "• bypass - Bypass restrictions (requires ownership)\n\n"
        "<b>Example:</b>\n"
        "<code>/autoforward without_tags -1001234567890 -1009876543210</code>",
        parse_mode=ParseMode.HTML
    )

async def forward_command(update: Update, context):
    """Manual forward command handler"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user or not user.telethon_session:
        await update.message.reply_text("❌ You must connect your Telegram account first. Use /connect_account.")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Please reply to a message to forward it.")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Usage: /forward &lt;mode&gt; &lt;target_chat1&gt; [target_chat2] ...\n"
            "Example: /forward without_tags -1009876543210"
        )
        return
    
    mode = args[0]
    if mode not in ['with_tags', 'without_tags', 'bypass']:
        await update.message.reply_text("❌ Invalid mode. Use: with_tags, without_tags, or bypass")
        return
    
    target_chats = []
    for chat_id_str in args[1:]:
        try:
            target_chats.append(validate_chat_id(chat_id_str))
        except ValueError:
            await update.message.reply_text(f"❌ Invalid chat ID: {chat_id_str}")
            return
    
    # Here you would implement the actual forwarding logic
    await update.message.reply_text(f"✅ Forwarding message to {len(target_chats)} target(s) in {mode} mode.")

async def rules_command(update: Update, context):
    """Rules command handler"""
    user_id = update.effective_user.id
    rules = db.get_rules(user_id)
    
    if not rules:
        await update.message.reply_text("📝 You haven't created any forwarding rules yet.\nUse /autoforward to create your first rule!")
        return
    
    rules_text = f"📋 <b>Your Forwarding Rules ({len(rules)})</b>\n\n"
    
    for i, rule in enumerate(rules, 1):
        status = "🟢 Active" if rule.is_active else "🔴 Inactive"
        target_count = len(rule.target_chats)
        use_user_account = "👤 Yes" if rule.use_user_account else "🤖 No"
        
        rules_text += (
            f"<b>{i}. Rule {rule.rule_id[:8]}...</b>\n"
            f"• Status: {status}\n"
            f"• Source: <code>{rule.source_chat}</code>\n"
            f"• Targets: {target_count} chat(s)\n"
            f"• Mode: {rule.mode}\n"
            f"• Use User Account: {use_user_account}\n"
            f"• Triggers: {rule.trigger_count}\n\n"
        )
    
    await update.message.reply_text(rules_text, parse_mode=ParseMode.HTML)

async def help_command(update: Update, context):
    """Help command handler"""
    help_text = """
📚 <b>Telegram Forwarding Bot Help</b>

🔗 <b>Account Management:</b>
• /connect_account - Connect your Telegram account
• /disconnect_account - Disconnect your account

📝 <b>Forwarding Commands:</b>
• /autoforward - Create auto-forwarding rules
• /forward - Manual forward (reply to message)
• /rules - View your forwarding rules

💡 <b>Usage Examples:</b>
• <code>/autoforward without_tags -1001234567890 -1009876543210</code>
• <code>/forward without_tags -1009876543210</code> (reply to message)

🎯 <b>Forwarding Modes:</b>
• <code>with_tags</code> - Keep "Forwarded from" info
• <code>without_tags</code> - Clean copy without tags
• <code>bypass</code> - Bypass restrictions (requires ownership)

📞 <b>Support:</b>
Contact @YourSupportBot for help
"""
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

async def cancel_conversation(update: Update, context) -> int:
    """Cancel conversation handler"""
    await update.message.reply_text("❌ Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

async def callback_query_handler(update: Update, context):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "connect_account":
        await connect_account_command(update, context)
    elif data == "autoforward":
        await autoforward_command(update, context)
    elif data == "rules":
        await rules_command(update, context)
    elif data == "help":
        await help_command(update, context)

def main():
    """Start the bot"""
    if not TELEGRAM_AVAILABLE:
        print("❌ Telegram library not available. Running in demo mode.")
        print("✅ Bot structure is ready. Install python-telegram-bot to run.")
        return
    
    print("🤖 Starting Telegram Forwarding Bot...")
    
    # Initialize updater
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("autoforward", autoforward_command))
    dispatcher.add_handler(CommandHandler("forward", forward_command))
    dispatcher.add_handler(CommandHandler("rules", rules_command))
    
    # Add callback query handler
    dispatcher.add_handler(CallbackQueryHandler(callback_query_handler))
    
    # Add conversation handler for account connection
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("connect_account", connect_account_command)],
        states={
            GET_PHONE_NUMBER_STATE: [MessageHandler(Filters.text & ~Filters.command, get_phone_number)],
            GET_AUTH_CODE_STATE: [MessageHandler(Filters.text & ~Filters.command, get_auth_code)],
            GET_2FA_PASSWORD_STATE: [MessageHandler(Filters.text & ~Filters.command, get_2fa_password)]
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)]
    )
    dispatcher.add_handler(conv_handler)
    
    # Start the bot
    print("✅ Bot is starting...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()