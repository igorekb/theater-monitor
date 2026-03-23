# Quick Start

## Setup (One Time)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # fill in bot token and channel IDs
```

### Verify Telegram connection
```bash
python test_channel_connection.py --test
```
If you see "✅ All tests PASSED!" you're ready.

---

## Running

```bash
# First run on new server — populate state without sending notifications
python main.py --no-notify

# Normal run — sends to production channel
python main.py

# Test run — sends to test channel (messages prefixed with 🧪 [TEST])
python main.py --test-channel
```

---

## Cron (Every 6 Hours)

```bash
crontab -e
```
```
0 */6 * * * cd /path/to/theater-monitor && venv/bin/python main.py >> logs/cron.log 2>&1
```

---

## Useful Commands

```bash
# Check logs
tail -f logs/theater_monitor.log

# See how many events are tracked
python manage_processed_ids.py --show

# Reset state (next run re-notifies everything — use --no-notify after reset)
python manage_processed_ids.py --clear

# Diagnose Telegram issues
python test_channel_connection.py

# Find channel Chat IDs
python get_channel_id.py
```

---

## Common Issues

**Getting 100+ notifications on first run?**
→ Use `python main.py --no-notify` on first run to silently populate state.

**Bot not sending messages?**
→ Run `python test_channel_connection.py` — it will tell you exactly what's wrong.

**Check logs for errors:**
```bash
tail -50 logs/theater_monitor.log
```
