# Quick Setup Guide for Test Channel

## Step-by-Step Instructions

### 1. Add Bot to Test Channel
1. Open the test channel: https://t.me/+rOY2zTmEcNo0ZGIy
2. Add your bot as an administrator to this channel
3. Give the bot permission to "Post messages"

### 2. Get the Channel Chat ID

Run the helper script after sending a message to the channel:

```bash
python get_channel_id.py
```

The script will show you the Chat ID and username of all channels where your bot is an admin.

### 2b. Verify Connection (Recommended)

Test the connection to your test channel:

```bash
# Test only the test channel
python test_channel_connection.py --test

# Or test both production and test channels
python test_channel_connection.py

# Or test only production channel
python test_channel_connection.py --production
```

This will verify:
- ✅ Bot token is valid
- ✅ Bot has access to the channel
- ✅ Bot has correct permissions
- ✅ Bot can send messages

### 3. Update Your .env File

Add these lines to your `.env` file (create from .env.example if needed):

```env
# Test channel configuration
TEST_TELEGRAM_CHAT_ID=-1001234567890
TEST_TELEGRAM_CHANNEL_USERNAME=@your_test_channel_name
```

Replace the values with what you got from `get_channel_id.py`.

### 4. Test It!

Run the monitor with the `--test-channel` flag:

```bash
# Test with puppet-minsk.by only
python main.py --puppet-only --test-channel

# Test with tce.by only (may take a few minutes)
python main.py --tce-only --test-channel

# Test both sites
python main.py --test-channel
```

### What to Expect

- Messages sent to the test channel will have a 🧪 [TEST] prefix
- The message will include a link to subscribe to the test channel (not production)
- All monitoring logic works the same, only the destination changes
- You can safely test without affecting your production channel subscribers

### Troubleshooting

**Run the diagnostic script first:**
```bash
python test_channel_connection.py --test
```

This will tell you exactly what's wrong!

**Common Issues:**

**"Channel ID not found"**
- Make sure the bot is added as administrator to the channel
- Send at least one message to the channel
- Run `get_channel_id.py` again

**"Bot token not found"**
- Make sure you have a `.env` file (copy from `.env.example`)
- Add your `TELEGRAM_BOT_TOKEN` to the `.env` file

**"400 Bad Request" error**
- Chat ID is wrong or in wrong format (should be like -1001234567890)
- Run `python test_channel_connection.py --test` to diagnose

**"403 Forbidden" error**
- Bot doesn't have permissions
- Make bot an administrator with "Post messages" permission

**No notification sent**
- Check logs in `logs/theater_monitor.log`
- Run `python test_channel_connection.py --test` for detailed diagnosis
- Verify the bot has "Post messages" permission in the channel
- Verify the Chat ID is correct (should be a negative number like -1001234567890)

### Example Complete .env File

```env
# Production Telegram settings
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001111111111
TELEGRAM_CHANNEL_USERNAME=@my_production_channel

# Test Telegram channel settings
TEST_TELEGRAM_CHAT_ID=-1002222222222
TEST_TELEGRAM_CHANNEL_USERNAME=@my_test_channel

# Browser automation settings
USE_HEADLESS=true
BROWSER_TIMEOUT=30
```

## Daily Usage

**For testing:**
```bash
python main.py --test-channel
```

**For production:**
```bash
python main.py
```

That's it! You're ready to test safely. 🎭
