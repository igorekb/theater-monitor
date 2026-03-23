# Changelog

## Current Architecture

The monitor uses a **search API** approach — no ID scanning, no HTML parsing.

### How it works
1. Playwright navigates to `tce.by` (bypasses Anubis JS challenge)
2. POST to `/index.php?view=shows&action=find&kind=text` with `server_key` filter — one request per calendar month
3. Stop at first empty month (typically 3–4 requests per run)
4. Compare `bk_id` values against `data/tce_processed_ids.json`
5. Build notification from API fields (`show_name`, `bk_date`, `hall_name`, `owner_name`)
6. Send to Telegram immediately per new event
7. Save updated processed IDs

### Key files
- `tce_monitor.py` — all monitoring logic
- `main.py` — entry point (`--test-channel`, `--no-notify`)
- `config.py` — `TCE_BASE_PARAM`, `TCE_MONTHS_AHEAD`
- `data/tce_processed_ids.json` — deduplication state
- `data/tce_events.json` — event audit log

---

## History (summarised)

| Change | Details |
|--------|---------|
| Replaced puppet-minsk.by pipeline | Site blocked the IP; monitoring moved entirely to tce.by |
| Replaced ID scanning with search API | `/index.php?view=shows&action=find&kind=text` returns all puppet theatre events directly |
| Added month-by-month requests | API caps at 100 results; ~50 events/month requires batching |
| Added stop-early on empty month | Avoids querying months with no events |
| Human-like Playwright behaviour | Random delays, nav path, `navigator.webdriver` patch, XHR headers |
| Added `--no-notify` flag | Silent first-run to populate state without spamming Telegram |
