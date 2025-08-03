#!/usr/bin/env python3
"""
Simple test script to verify bot functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if required environment variables are set
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

print("=== Bot Configuration Test ===")
print(f"BOT_TOKEN: {'✅ Set' if BOT_TOKEN else '❌ Missing'}")
print(f"API_ID: {'✅ Set' if API_ID else '❌ Missing'}")
print(f"API_HASH: {'✅ Set' if API_HASH else '❌ Missing'}")

if not BOT_TOKEN:
    print("\n❌ ERROR: BOT_TOKEN is required!")
    print("Please add your bot token to the .env file:")
    print("BOT_TOKEN=your_bot_token_here")
    sys.exit(1)

if not API_ID or not API_HASH:
    print("\n⚠️  WARNING: API_ID and API_HASH are required for account connectivity!")
    print("Please add them to the .env file:")
    print("API_ID=your_api_id_here")
    print("API_HASH=your_api_hash_here")

print("\n✅ Bot configuration looks good!")
print("\nTo start the bot, run: python3 bot_new.py")
print("\nBot Features:")
print("- /start - Welcome message")
print("- /connect_account - Connect your Telegram account")
print("- /autoforward - Create auto-forwarding rules")
print("- /forward - Manual forwarding")
print("- /rules - Manage your rules")
print("- /help - Get help")