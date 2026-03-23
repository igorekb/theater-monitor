# Theater Monitor

Monitors [tce.by](https://tce.by) for new puppet theatre events and sends instant Telegram notifications. Runs as a cron job.

## Features

- **Search API monitoring** — queries tce.by search API month-by-month, stops as soon as an empty month is found
- **Anubis bypass** — uses Playwright (headless Chromium) to pass the JS proof-of-work challenge
- **Human-like behaviour** — randomised delays, mouse movement, realistic browser fingerprint
- **Deduplication** — tracks processed event IDs so each event is notified exactly once
- **Test channel support** — send to a separate Telegram channel for testing

## Requirements

- Python 3.8+
- Playwright (`pip install playwright && playwright install chromium`)
- Telegram bot token + channel

## Installation

```bash
git clone https://github.com/igorekbs/theater-monitor.git
cd theater-monitor

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

cp .env.example .env   # then fill in credentials
```

### `.env` variables

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=-100...
TELEGRAM_CHANNEL_USERNAME=@your_channel

# Optional: separate test channel
TEST_TELEGRAM_CHAT_ID=-100...
TEST_TELEGRAM_CHANNEL_USERNAME=@your_test_channel

# Browser settings
USE_HEADLESS=true
BROWSER_TIMEOUT=30
```

## Usage

```bash
# Normal run — fetches events, sends Telegram notifications
python main.py

# First run on a new server — populates state without sending notifications
python main.py --no-notify

# Send to test channel instead of production
python main.py --test-channel
```

## First Run (New Server Setup)

On first run all existing events would trigger notifications. Use `--no-notify` to silently populate the state files, then let the cron job take over:

```bash
python main.py --no-notify   # fills tce_processed_ids.json silently
# cron runs from here — only new events trigger notifications
```

## Deployment (Cron)

```bash
crontab -e
```

```
0 */6 * * * cd /path/to/theater-monitor && venv/bin/python main.py >> logs/cron.log 2>&1
```

## Utility Scripts

```bash
python manage_processed_ids.py --show    # view processed event count and IDs
python manage_processed_ids.py --clear   # reset state (next run re-notifies all)
python test_channel_connection.py        # diagnose Telegram bot connectivity
python get_channel_id.py                 # discover Telegram channel Chat IDs
```

## Architecture

```
main.py
  └─ tce_monitor.check_for_new_tce_events()
       ├─ _fetch_search_api_with_playwright()
       │    ├─ Navigate tce.by (Anubis bypass via Playwright)
       │    └─ POST /index.php?view=shows&action=find&kind=text
       │         one request per calendar month, stop at first empty month
       ├─ load_processed_ids()           data/tce_processed_ids.json
       ├─ _build_event_from_api()        parse bk_id, show_name, bk_date, hall_name...
       ├─ notify_tce_event_immediately() Telegram HTML message per new event
       └─ save_processed_ids()
```

**State files in `data/`:**
- `tce_processed_ids.json` — set of `bk_id` values already notified
- `tce_events.json` — full event details (audit log)

**Config in `config.py`:**
- `TCE_BASE_PARAM` — server_key identifying the puppet theatre
- `TCE_MONTHS_AHEAD` — how many future months to scan (default: 4)

## Troubleshooting

**Anubis blocking requests**
```bash
# Run in visible browser to watch the challenge
USE_HEADLESS=false python main.py --no-notify
```

**Telegram rate limit (429)**
The monitor sends one notification per event. If you reset state and re-run without `--no-notify`, many messages will be sent at once. Always use `--no-notify` for initial population.

**Check logs**
```bash
tail -f logs/theater_monitor.log
```

## License

MIT
