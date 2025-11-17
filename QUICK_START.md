# Quick Start Guide

## Initial Setup (One Time)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Bot Token
```bash
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN
```

### 3. Setup Test Channel
```bash
# Add bot to test channel as admin, then:
python get_channel_id.py

# Copy the Chat ID and add to .env:
# TEST_TELEGRAM_CHAT_ID=-1001234567890
```

### 4. Test Connection
```bash
# Test that everything works
python test_channel_connection.py --test
```

If you see "✅ All tests PASSED!", you're ready to go!

---

## Daily Usage Commands

### Testing (Safe - Won't Affect Production)

```bash
# Test both sites with test channel
python main.py --test-channel

# Test only puppet-minsk.by
python main.py --puppet-only --test-channel

# Test only tce.by
python main.py --tce-only --test-channel
```

### Production (Sends to Real Channel)

```bash
# Monitor both sites
python main.py

# Monitor only puppet-minsk.by
python main.py --puppet-only

# Monitor only tce.by
python main.py --tce-only
```

---

## Troubleshooting Commands

### Check Channel Connection
```bash
# Diagnose test channel issues
python test_channel_connection.py --test

# Diagnose production channel issues
python test_channel_connection.py --production

# Check both channels
python test_channel_connection.py
```

### Get Channel Chat ID
```bash
python get_channel_id.py
```

### Check Logs
```bash
# View recent logs
tail -50 logs/theater_monitor.log

# Follow logs in real-time
tail -f logs/theater_monitor.log
```

---

## Common Scenarios

### "I want to test without sending to production"
```bash
python main.py --test-channel
```

### "I only want to check puppet-minsk.by"
```bash
python main.py --puppet-only --test-channel
```

### "I'm getting 400 Bad Request errors"
```bash
# Run diagnostics
python test_channel_connection.py --test

# Most common issue: Chat ID not configured
# Fix: Run get_channel_id.py and update .env
```

### "How do I know if bot has correct permissions?"
```bash
python test_channel_connection.py --test
```
This will show:
- ✅ Bot is administrator
- ✅ Bot CAN post messages
- ❌ Bot CANNOT post messages ← Fix this!

### "I want to scan more TCE event IDs"
```bash
python main.py --tce-only --tce-start-id 4080 --tce-range 20 --test-channel
```

---

## Files You Need to Configure

1. **`.env`** - Your credentials (copy from .env.example)
   ```env
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_CHAT_ID=production_chat_id
   TEST_TELEGRAM_CHAT_ID=test_chat_id
   ```

2. **`config.py`** - Advanced settings (optional)
   - TCE_START_ID - Where to start scanning
   - TCE_ID_RANGE - How many IDs to check

---

## What Each Script Does

| Script | Purpose |
|--------|---------|
| `main.py` | Main monitor - checks for new performances/events |
| `test_channel_connection.py` | Diagnose connection issues |
| `get_channel_id.py` | Find channel Chat IDs |
| `manage_tce_id.py` | View/set TCE last checked ID |
| `test_channel.py` | Simple test notification |
| `test_telegram.py` | Test Telegram API |

## Managing TCE ID Tracking

```bash
# View current last checked ID
python manage_tce_id.py

# Set starting ID (useful for testing)
python manage_tce_id.py --set 4070

# Reset to default from config
python manage_tce_id.py --reset
```

---

## Help!

**Getting errors?**
1. Run: `python test_channel_connection.py --test`
2. Read the error messages - they'll tell you exactly what's wrong
3. Fix the issue (usually permissions or Chat ID)
4. Try again

**Still stuck?**
- Check `logs/theater_monitor.log`
- Read `TEST_CHANNEL_SETUP.md` for detailed setup
- Make sure bot is admin with "Post messages" permission
