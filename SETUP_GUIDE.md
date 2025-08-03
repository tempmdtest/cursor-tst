# Telegram Forwarding Bot Setup Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Edit the `.env` file with your credentials:

```env
# Get from @BotFather on Telegram
BOT_TOKEN=your_bot_token_here

# Get from https://my.telegram.org/apps
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Your Telegram user ID (optional, for owner features)
OWNER_ID=your_telegram_user_id_here
```

### 3. Run the Bot
```bash
python3 bot_new.py
```

## 📋 Getting Your Credentials

### Bot Token
1. Message @BotFather on Telegram
2. Send `/newbot`
3. Follow the instructions to create your bot
4. Copy the token provided

### API Credentials
1. Go to https://my.telegram.org/apps
2. Log in with your phone number
3. Create a new application
4. Copy the `api_id` and `api_hash`

## 🔧 Features

### ✅ Implemented Features

#### Account Connectivity
- **Connect Account**: `/connect_account` - Connect your personal Telegram account
- **Disconnect Account**: `/disconnect_account` - Disconnect your account
- **2FA Support**: Full two-factor authentication support
- **Session Management**: Secure session storage

#### Auto-Forwarding
- **Create Rules**: `/autoforward` - Create automatic forwarding rules
- **Three Modes**:
  - `with_tags` - Keep "Forwarded from" information
  - `without_tags` - Clean copy without forward tags
  - `bypass` - Bypass restrictions (requires ownership)
- **Keyword Filtering**: Filter messages by keywords
- **Schedule Support**: Set forwarding schedules
- **Media Filtering**: Filter by media type

#### Manual Forwarding
- **Forward Command**: `/forward` - Manually forward messages
- **Multiple Targets**: Forward to multiple chats at once
- **User Account Integration**: Use connected accounts for advanced forwarding

#### Rule Management
- **List Rules**: `/rules` - View and manage your rules
- **Edit Rules**: Modify existing rules
- **Delete Rules**: Remove unwanted rules
- **Rule Statistics**: Track rule performance

#### User Management
- **User Settings**: `/user_settings` - Configure your preferences
- **Statistics**: `/stats` - View your forwarding statistics
- **Logs**: `/logs` - View your activity logs

#### Admin Features
- **User Management**: `/users` - View all users
- **Promote/Demote**: Manage user roles
- **Ban/Unban**: Manage user access
- **Broadcast**: Send messages to all users
- **System Stats**: Monitor bot performance

### 🔄 How It Works

1. **Account Connection**: Users connect their Telegram accounts using Telethon
2. **Rule Creation**: Users create forwarding rules with source and target chats
3. **Auto-Forwarding**: The bot automatically forwards messages based on rules
4. **Manual Forwarding**: Users can manually forward specific messages
5. **User Account Integration**: Rules can use connected accounts for advanced forwarding

## 🛠️ Troubleshooting

### Common Issues

#### Bot Not Starting
- Check if BOT_TOKEN is set correctly
- Verify API_ID and API_HASH are correct
- Ensure all dependencies are installed

#### Account Connection Issues
- Make sure API_ID and API_HASH are from https://my.telegram.org/apps
- Check if your phone number is correct
- Verify 2FA password if enabled

#### Forwarding Not Working
- Ensure you have permission in source and target chats
- Check if the rule is active
- Verify chat IDs are correct

### Logs
- Check `bot.log` for detailed error messages
- Use `/debug` command for system information
- Monitor console output for warnings

## 📊 Database

The bot uses SQLite database (`bot_data.db`) to store:
- User profiles and settings
- Forwarding rules
- Activity logs
- Statistics
- Global settings

## 🔒 Security

- Session strings are encrypted
- User data is protected
- Rate limiting prevents abuse
- Admin-only features are protected

## 📈 Performance

- Efficient message processing
- Database optimization
- Memory management
- Background cleanup jobs

## 🆘 Support

If you encounter issues:
1. Check the logs in `bot.log`
2. Verify your credentials in `.env`
3. Test with `/debug` command
4. Check the README.md for detailed feature documentation