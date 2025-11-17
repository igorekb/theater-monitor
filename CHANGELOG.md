# Changelog

## [Latest Update] - TCE.BY Smart Range Scanning

### Changed
- **Improved TCE ID Checking Logic**
  - Now checks 10 IDs ahead of last found event (base ID)
  - When event found, updates base to that ID and checks 10 more
  - Stops only when no events found in 10 ID range
  - **No IDs are skipped** - always validates full range
  - More efficient for sparse event distributions

- **Better Progress Tracking**
  - Saves highest found event ID as base
  - Next run checks from that base again
  - Ensures complete coverage even with ID gaps

### Example
```
Old logic (consecutive 404s):
Check 4070, 4071, 4072... stop after 10 consecutive 404s
May miss events if there are gaps

New logic (range-based):
Base: 4070
Check 4071-4080 → Found 4073, 4075
Base: 4075
Check 4076-4085 → Found 4082
Base: 4082
Check 4083-4092 → No events
Stop at 4082
```

---

## [Previous Update] - TCE.BY Date/Time Extraction

### Added
- **Smart Date/Time Extraction** for TCE.BY events
  - Primary pattern: "Начало DD.MM.YYYY в HH:MM"
  - Fallback patterns for separate date and time
  - Case-insensitive matching
  - Example: "Начало 07.01.2026 в 15:45" → Date: 07.01.2026, Time: 15:45

- **Enhanced Notification Display**
  - Combined date/time display: "📅 07.01.2026 в 15:45"
  - Graceful handling when only date or time available
  - Better notification formatting for TCE events

- **Test Script** (`test_tce_date_extraction.py`)
  - Validates date/time extraction with multiple test cases
  - Covers edge cases and fallback patterns
  - All 6 test cases passing

### Changed
- **TCE Notification Message**
  - Now shows "НОВОЕ МЕРОПРИЯТИЕ TCE.BY!" to distinguish from puppet-minsk
  - Date and time combined on single line when both available
  - Description limited to 300 characters for better readability

### Technical Details
- Added `extract_date_time_from_text()` function in `tce_monitor.py`
- Uses regex patterns for flexible date/time matching
- Improved logging to show extracted date/time values

---

## [Previous Update] - TCE.BY Immediate Notifications

### Added
- **Immediate Telegram notifications** when TCE events found
- **Progressive ID scanning** with smart continuation
- **Persistent progress tracking** in `data/tce_last_id.json`
- **Smart 404 handling** - resets counter when event found
- Helper script `manage_tce_id.py` to view/set last checked ID

### Changed
- TCE events now sent immediately (not batched)
- Search continues from last found ID
- Stops after N consecutive 404s (default: 10)

---

## Features Summary

### Multi-Site Monitoring
- ✅ puppet-minsk.by (batch notifications)
- ✅ tce.by (immediate notifications with date/time extraction)

### Anubis Protection Bypass
- ✅ Playwright (recommended)
- ✅ Selenium (fallback)
- ✅ Requests (last resort)

### Smart Parsing
- ✅ Multiple CSS selector fallbacks
- ✅ Structural HTML analysis
- ✅ Pattern-based extraction (dates, times, Russian months)
- ✅ Design change resilience

### Testing Tools
- ✅ `test_channel_connection.py` - Connection diagnostics
- ✅ `get_channel_id.py` - Find channel IDs
- ✅ `manage_tce_id.py` - Manage TCE progress
- ✅ `test_tce_date_extraction.py` - Verify date parsing

### Documentation
- ✅ README.md - Complete guide
- ✅ QUICK_START.md - Quick reference
- ✅ TEST_CHANNEL_SETUP.md - Test channel setup
- ✅ TCE_IMMEDIATE_NOTIFICATIONS.md - TCE system details
- ✅ CHANGELOG.md - This file
