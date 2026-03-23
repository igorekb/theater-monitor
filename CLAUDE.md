# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env  # then fill in credentials
```

## Running

```bash
python main.py                    # Run monitor (sends to production channel)
python main.py --test-channel     # Send to test Telegram channel instead of production
python main.py --no-notify        # Collect and save events without sending any Telegram notifications
                                  # Use on first run to populate state without spamming the channel
```

## Utility Scripts

```bash
python manage_processed_ids.py --show   # View count and IDs of already-processed events
python manage_processed_ids.py --clear  # Reset state (next run re-notifies all events)
python test_channel_connection.py       # Diagnose Telegram bot connectivity
python get_channel_id.py                # Get Telegram chat IDs
```

## Architecture

Cron-driven polling app. Monitors tce.by for puppet theatre events via a search API
and sends Telegram notifications when new events appear. No server, no test framework.

**Single monitoring pipeline:**

`tce_monitor.py` → search API → filter new → notify → save state

1. Launch Playwright (headless Chromium), navigate to `tce.by` homepage then `search.html`
   to pass the Anubis JS proof-of-work challenge.
2. Call the search API from within the browser context (reuses Anubis clearance cookie):
   `POST /index.php?view=shows&action=find&kind=text` with `server_key=TCE_BASE_PARAM`
3. Fetch one request per calendar month (current + up to `TCE_MONTHS_AHEAD` future months).
   Stop at the first month that returns 0 events.
4. Compare returned `bk_id` values against `data/tce_processed_ids.json`.
5. For each new event, build notification from API fields (`show_name`, `bk_date`,
   `hall_name`, `hall_address`, `owner_name`) and send to Telegram immediately.
6. Save all seen IDs to state file.

**Key files:**
- `main.py` — entry point, CLI args, logging setup
- `config.py` — all URLs, keys, Telegram credentials (sourced from `.env`)
- `tce_monitor.py` — Anubis bypass, search API fetch, event dedup, Telegram dispatch

**Anti-bot measures in `tce_monitor.py`:**
- Playwright with `--disable-blink-features=AutomationControlled`
- `add_init_script` patches `navigator.webdriver`, `plugins`, `chrome` object
- Navigate homepage → search page (natural browsing path)
- Random delays throughout (Anubis wait 4–8s, between API calls 1.5–4s)
- Scroll + mouse move after page load
- XHR headers (`X-Requested-With`, `Accept`) on API calls

**State files** in `data/`:
- `tce_processed_ids.json` — set of `bk_id` values already notified (prevents duplicates)
- `tce_events.json` — full event details cache (audit log of all found events)

**Logs** written to `logs/theater_monitor.log` and console.

## Deployment

Intended to run via cron (e.g., every 6 hours):
```
0 */6 * * * cd /path/to/theater-monitor && venv/bin/python main.py >> logs/cron.log 2>&1
```
