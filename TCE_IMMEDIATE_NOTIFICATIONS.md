# TCE.BY Immediate Notification System

## Overview

The TCE.BY monitoring system now uses **immediate notifications** - events are posted to Telegram as soon as they're discovered, and the search automatically continues from each found event.

## How It Works

### Progressive ID Scanning

1. **Start Point**: Begins from base ID (last found event or config default)
2. **Check Range**: Checks next 10 IDs from base (base+1 to base+10)
3. **For Each ID in Range**:
   - Fetch and parse the event page
   - **If Event Found**:
     - ✅ Send Telegram notification immediately
     - ✅ Save event to database
     - ✅ Mark as found, track highest ID
   - **If 404**: Continue to next ID in range
4. **After Checking Full Range**:
   - **If any events found**:
     - Set highest found ID as new base
     - Check next 10 IDs from new base
     - Repeat process
   - **If no events found**:
     - Stop checking
     - Save current base for next run
5. **Result**: Always checks 10 IDs ahead of last found event until no more events in range

### Example Flow

```
Starting from base ID: 4070
TCE_ID_RANGE: 10

🔍 Check IDs 4071-4080 (next 10 from base 4070):
   ID 4071 → 404
   ID 4072 → 404
   ID 4073 → Event found: "Concert A" ✅ Send notification
   ID 4074 → 404
   ID 4075 → Event found: "Theater B" ✅ Send notification
   ID 4076 → 404
   ID 4077 → 404
   ID 4078 → 404
   ID 4079 → 404
   ID 4080 → 404

✅ Found events! Highest at ID 4075
📌 New base: 4075

🔍 Check IDs 4076-4085 (next 10 from base 4075):
   ID 4076 → 404
   ID 4077 → 404
   ID 4078 → 404
   ID 4079 → 404
   ID 4080 → 404
   ID 4081 → 404
   ID 4082 → Event found: "Show C" ✅ Send notification
   ID 4083 → 404
   ID 4084 → 404
   ID 4085 → 404

✅ Found events! Highest at ID 4082
📌 New base: 4082

🔍 Check IDs 4083-4092 (next 10 from base 4082):
   ID 4083 → 404
   ID 4084 → 404
   ID 4085 → 404
   ID 4086 → 404
   ID 4087 → 404
   ID 4088 → 404
   ID 4089 → 404
   ID 4090 → 404
   ID 4091 → 404
   ID 4092 → 404

❌ No events found in this range
🛑 Stop checking

Save base ID: 4082
Next run starts from: 4082 (will check 4083-4092 again)
```

## Key Features

### 1. Immediate Notifications
- Events are sent to Telegram **instantly** when discovered
- No waiting for batch processing
- Faster alerts for time-sensitive events

### 2. Smart Continuation
- When an event is found at ID X, continues checking from X+1
- Doesn't stop just because one event was found
- Keeps checking until hitting consecutive 404s threshold

### 3. Persistent Progress
- Tracks last checked ID in `data/tce_last_id.json`
- Automatically resumes from where previous run stopped
- No duplicate checks across runs

### 4. Configurable Threshold
- `TCE_ID_RANGE` controls how many consecutive 404s before stopping
- Default: 10 consecutive 404s
- Higher = more thorough but slower
- Lower = faster but might miss events with gaps

## Configuration

### In `config.py`:

```python
TCE_START_ID = 4070      # Initial starting point (first run only)
TCE_ID_RANGE = 10        # Stop after N consecutive 404s
```

### Last Checked ID:

The system automatically manages `data/tce_last_id.json`:

```json
{
  "last_checked_id": 4084
}
```

## Usage

### Normal Operation

```bash
# Test channel (recommended first)
python main.py --tce-only --test-channel

# Production channel
python main.py --tce-only
```

### Managing the Last Checked ID

```bash
# View current ID
python manage_tce_id.py

# Set specific ID (useful for testing or reset)
python manage_tce_id.py --set 4070

# Reset to config default
python manage_tce_id.py --reset

# Delete tracking (start fresh)
python manage_tce_id.py --delete
```

## Differences from Batch Mode

### Old Behavior (Puppet-Minsk):
```
1. Check all performances
2. Compare with previous data
3. Find new ones
4. Send ONE notification with all new performances
```

### New Behavior (TCE.BY):
```
1. Check ID 4070 → Found → Send notification #1
2. Check ID 4071 → 404
3. Check ID 4072 → Found → Send notification #2
4. Continue until 10 consecutive 404s
5. Save progress for next run
```

## Benefits

### ✅ Real-Time Alerts
- Events appear in Telegram immediately
- No delay waiting for batch processing

### ✅ Continuous Discovery
- Doesn't stop after first event
- Finds all available events in one run
- Automatically handles gaps in ID sequence

### ✅ Efficient Resumption
- Next run starts exactly where previous stopped
- No wasted checks on already-processed IDs
- Perfect for scheduled (cron) execution

### ✅ Handles Sparse IDs
- If events are at IDs 4070, 4075, 4090
- Will find all three in one run
- Continues through gaps until hitting threshold

## Testing

### Test with Low ID Range

For faster testing, temporarily lower the threshold:

1. Edit `config.py`:
   ```python
   TCE_ID_RANGE = 3  # Stop after just 3 consecutive 404s
   ```

2. Run test:
   ```bash
   python main.py --tce-only --test-channel
   ```

3. Watch the logs to see immediate notifications

### Simulate Finding Multiple Events

```bash
# Set starting ID
python manage_tce_id.py --set 4070

# Run monitor
python main.py --tce-only --test-channel

# Check what ID it stopped at
python manage_tce_id.py

# Run again - it continues from where it left off
python main.py --tce-only --test-channel
```

## Monitoring Logs

Watch the logs to see the process:

```bash
tail -f logs/theater_monitor.log
```

You'll see:
```
Starting TCE ID check from 4070, will stop after 10 consecutive 404s
Checking TCE ID 4070...
✅ Found valid event at ID 4070: Concert Title
✅ Immediate notification sent for TCE event ID 4070
Saved new TCE event ID 4070 to database
Event found! Resetting 404 counter. Will continue checking...
Checking TCE ID 4071...
❌ No valid event at ID 4071 (404 #1/10)
...
```

## Troubleshooting

### Notifications Not Sending

Check test channel connection:
```bash
python test_channel_connection.py --test
```

### Stuck at Same ID

View current ID:
```bash
python manage_tce_id.py
```

If stuck, reset:
```bash
python manage_tce_id.py --set 4070
```

### Too Many/Few Checks

Adjust `TCE_ID_RANGE` in `config.py`:
- Increase: More thorough (checks more after last event)
- Decrease: Faster (stops sooner after last event)

## Production Deployment

For scheduled execution (cron), the system automatically:
1. Resumes from last checked ID
2. Finds and notifies new events immediately
3. Saves progress for next run
4. Stops after threshold met

Perfect for:
```cron
# Check every 6 hours
0 */6 * * * /path/to/theater-monitor/run_monitor.sh
```

Each run efficiently continues from where the last run stopped!

## Date and Time Extraction

The TCE monitor intelligently extracts date and time from the event page:

### Extraction Patterns

**Primary Pattern:** "Начало DD.MM.YYYY в HH:MM"
- Example: "Начало 07.01.2026 в 15:45"
- Extracts: Date = "07.01.2026", Time = "15:45"
- Case-insensitive matching

**Fallback Pattern:** Separate date and time
- Date pattern: "DD.MM.YYYY" (anywhere in text)
- Time pattern: "HH:MM" (anywhere in text)
- Works when date and time are in different parts of the page

### Notification Display

The date and time are displayed clearly in notifications:

- **Both available:** "📅 07.01.2026 в 15:45"
- **Date only:** "📅 07.01.2026"
- **Time only:** "🕒 15:45"

### Example Notification

```
🎭 НОВОЕ МЕРОПРИЯТИЕ TCE.BY! 🎭

Концерт "Название"

📅 07.01.2026 в 15:45
📍 Venue Name

🎟 Подробнее и билеты

Event description preview...

➖➖➖➖➖➖➖➖➖➖➖➖
Подпишись @puppettesting для получения уведомлений!
```

### Testing Date Extraction

Run the test script to verify extraction:

```bash
python test_tce_date_extraction.py
```

This tests various date/time formats and edge cases.
