# Telegram Forwarding Bot

A comprehensive Telegram bot for automatic and manual message forwarding with user account connectivity.

## Features

### 🔗 Account Connectivity
- **Telethon Integration**: Connect your personal Telegram account to the bot
- **Secure Session Management**: Store encrypted session strings
- **2FA Support**: Full two-factor authentication support
- **Account Verification**: Verify ownership of source chats for bypass mode

### 📝 Auto-Forwarding Rules
- **Three Forwarding Modes**:
  - `with_tags` - Keep "Forwarded from" information
  - `without_tags` - Clean copy without forward tags
  - `bypass` - Bypass restrictions (requires ownership)
- **Rule Management**: Create, edit, and manage forwarding rules
- **User Account Integration**: Use connected accounts for advanced forwarding

### 🎯 Manual Forwarding
- **Reply-based Forwarding**: Reply to any message and forward it
- **Multiple Targets**: Forward to multiple chats simultaneously
- **Mode Selection**: Choose forwarding mode for each operation

### 👥 User Management
- **Role System**: Free, Premium, Admin, Owner roles
- **Phone Verification**: Optional phone number verification
- **User Profiles**: Track user activity and statistics

### 📊 Statistics & Monitoring
- **Forward Statistics**: Track successful and failed forwards
- **Rule Analytics**: Monitor rule performance
- **User Activity**: Track user engagement

## Installation

### Prerequisites
- Python 3.7+
- Telegram Bot Token
- Telegram API ID and API Hash

### Dependencies
```bash
pip install -r requirements.txt
```

### Configuration
1. Set your bot token in the configuration section
2. Add your API ID and API Hash
3. Set owner ID for admin access

## Usage

### Starting the Bot
```bash
python3 bot_simple.py
```

### Commands

#### Account Management
- `/connect_account` - Connect your Telegram account
- `/disconnect_account` - Disconnect your account

#### Forwarding Commands
- `/autoforward` - Create auto-forwarding rules
- `/forward` - Manual forward (reply to message)
- `/rules` - View your forwarding rules

#### Help & Support
- `/start` - Welcome message and quick start
- `/help` - Detailed help information

### Examples

#### Connect Account
1. Send `/connect_account`
2. Enter your phone number (e.g., +12345678900)
3. Enter the verification code from Telegram
4. If 2FA is enabled, enter your password

#### Create Auto-Forward Rule
```
/autoforward without_tags -1001234567890 -1009876543210
```
This creates a rule that forwards messages from source chat `-1001234567890` to target chat `-1009876543210` in clean mode.

#### Manual Forward
1. Reply to any message
2. Send `/forward without_tags -1009876543210`
3. The message will be forwarded to the specified chat

## Database Structure

### Users Table
- `user_id` - Telegram user ID
- `username` - Telegram username
- `first_name`, `last_name` - User names
- `phone` - Phone number
- `role` - User role (free/premium/admin/owner)
- `telethon_session` - Encrypted session string
- `total_forwards` - Number of forwards made
- `total_rules` - Number of rules created

### Rules Table
- `rule_id` - Unique rule identifier
- `user_id` - Owner of the rule
- `source_chat` - Source chat ID
- `target_chats` - JSON array of target chat IDs
- `mode` - Forwarding mode
- `is_active` - Rule status
- `use_user_account` - Whether to use user's account

## Security Features

- **Session Encryption**: All Telethon sessions are encrypted
- **Role-based Access**: Different permission levels
- **Input Validation**: All inputs are validated
- **Error Handling**: Comprehensive error handling

## Troubleshooting

### Common Issues

1. **Telegram library not available**
   - Install python-telegram-bot: `pip install python-telegram-bot==11.1.0`

2. **Telethon import errors**
   - Install Telethon: `pip install telethon==1.34.0`

3. **Database errors**
   - Check file permissions for bot_data.db
   - Ensure SQLite is available

4. **API errors**
   - Verify your API ID and API Hash
   - Check bot token validity

### Debug Mode
The bot includes comprehensive logging. Check the console output for detailed error messages.

## Development

### Adding New Features
1. Extend the data structures in the main file
2. Add new database tables if needed
3. Implement command handlers
4. Update the help documentation

### Testing
- Test with a development bot token
- Use test chat IDs for development
- Monitor logs for errors

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all dependencies are installed correctly

## License

This project is for educational and personal use. Please respect Telegram's terms of service and API usage guidelines.