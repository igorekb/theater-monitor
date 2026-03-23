# TCE.BY Monitoring Logic

## Overview

Events are discovered via a **search API** — one POST request per calendar month —
rather than scanning sequential numeric IDs. A processed-IDs set prevents duplicate
notifications across runs.

---

## Flow Per Run

```
1. Open Playwright browser (Anubis bypass)
   └─ Navigate to tce.by homepage → tce.by/search.html
      └─ Anubis JS proof-of-work completes (~4–8s)

2. For each month window (current month, +1, +2, ... up to TCE_MONTHS_AHEAD):
   └─ POST /index.php?view=shows&action=find&kind=text
      body: server_key=<TCE_BASE_PARAM>, date_begin=YYYY-MM-DD, date_end=YYYY-MM-DD
   └─ If response has 0 events → STOP (no point checking further months)
   └─ Collect all returned events, deduplicate by bk_id

3. Load data/tce_processed_ids.json  (set of already-seen bk_id values)

4. new_events = [e for e in fetched if e.bk_id not in processed_ids]

5. For each new event:
   └─ Build notification from API fields (no individual page fetch needed)
   └─ Send Telegram notification immediately
   └─ Append to data/tce_events.json

6. Save updated processed_ids (all fetched IDs, including already-seen)
```

---

## Month Window Visual

```
Today: 2026-03-23, TCE_MONTHS_AHEAD = 4

Request 1: date_begin=2026-03-23  date_end=2026-03-31  →  N events  → continue
Request 2: date_begin=2026-04-01  date_end=2026-04-30  →  N events  → continue
Request 3: date_begin=2026-05-01  date_end=2026-05-31  →  N events  → continue
Request 4: date_begin=2026-06-01  date_end=2026-06-30  →  0 events  → STOP
(Requests for July and beyond are skipped)
```

Note: The first month always starts from **today** (not the 1st) to skip past events.

---

## Deduplication

```
tce_processed_ids.json:
{
  "processed_ids": [4406, 4407, 4408, ..., 4644]
}
```

- On each run: `new = fetched_ids - processed_ids`
- After notifying: `processed_ids |= fetched_ids` (union — marks all current events as seen)
- An event is notified **exactly once**, even if it appears in multiple runs

---

## API Response Structure

```json
{
  "data": [
    {
      "bk_id":       4552,
      "server_key":  "RkZDMTE2MUQ...",
      "show_name":   "Название спектакля",
      "bk_date":     "2026-04-15 19:00:00",
      "hall_name":   "Название зала",
      "hall_address":"ул. Примерная, 1",
      "owner_name":  "Название театра"
    },
    ...
  ],
  "success": true
}
```

The `server_key` is sent as a POST parameter to filter server-side — only puppet
theatre events are returned. No client-side filtering is needed.

---

## Why Not ID Scanning?

The previous approach incremented numeric IDs (checking `?data=4071`, `?data=4072`, …)
and tracked a watermark. This was replaced because:

- The search API returns **all events directly** — no need to guess IDs
- Event data (title, date, venue) comes from the API — **no individual page fetches**
- Simpler state: a set of seen IDs vs. a fragile watermark that could skip events
- Fewer requests: 2–4 API calls per run vs. 10+ page loads

---

## Configuration

```python
# config.py
TCE_BASE_PARAM    = "RkZDMTE2MUQ..."  # puppet theatre server_key
TCE_SEARCH_API_URL = "https://tce.by/index.php?view=shows&action=find&kind=text"
TCE_MONTHS_AHEAD  = 4                 # current month + 4 future months (hard cap)
```

---

## State Files

| File | Purpose |
|------|---------|
| `data/tce_processed_ids.json` | Set of `bk_id` values already notified |
| `data/tce_events.json` | Full event details (audit log) |

Use `python manage_processed_ids.py --show` to inspect state,
`--clear` to reset (next run re-notifies all current events).
