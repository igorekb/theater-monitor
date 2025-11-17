# Theater Monitor

Multi-site theater performance monitoring app that tracks new performances from multiple theater websites and sends Telegram notifications.

## ✨ Features

- **Multi-Site Monitoring**: Supports both puppet-minsk.by and tce.by
- **Intelligent Parsing**: Resilient to website design changes with multiple fallback strategies
- **ID-Based Monitoring**: Checks incremental event IDs on tce.by to discover new events
- **Anubis Protection Bypass**: Uses browser automation (Playwright/Selenium) to bypass anti-bot protection
- **Telegram Notifications**: Automatic notifications for new performances/events
- **Flexible Configuration**: Command-line options and environment variables
- **Robust Error Handling**: Graceful degradation and detailed logging

## 🎭 Supported Sites

1. **puppet-minsk.by** - Puppet Theater performances
2. **tce.by** - Theater and cultural events (with Anubis protection bypass)

## 🔧 Requirements

- Python 3.7+
- Telegram bot token
- Telegram channel
- Linux VPS with cron (for scheduled execution)
- Browser automation tool (Playwright or Selenium) for tce.by monitoring

## 🏗️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/igorekbs/theater-monitor.git
cd theater-monitor
```

### 2. Create Virtual Environment and Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Browser for Playwright (if using Playwright)
```bash
playwright install chromium
```

**Alternative**: If you prefer Selenium, install Chrome/Chromium and ChromeDriver manually.

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your Telegram credentials
```

Configuration options in `.env`:
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token (same for production and test)
- `TELEGRAM_CHAT_ID` - Production channel chat ID
- `TELEGRAM_CHANNEL_USERNAME` - Production channel username (e.g., @your_channel)
- `TEST_TELEGRAM_CHAT_ID` - Test channel chat ID
- `TEST_TELEGRAM_CHANNEL_USERNAME` - Test channel username (e.g., @your_test_channel)
- `USE_HEADLESS` - Run browser in headless mode (default: true)
- `BROWSER_TIMEOUT` - Browser timeout in seconds (default: 30)

### 5. Configure Monitoring Parameters

Edit `config.py` to adjust:
- `TCE_START_ID` - Starting event ID for tce.by (default: 4070)
- `TCE_ID_RANGE` - Number of IDs to check (default: 10)
- `TCE_BASE_PARAM` - Base parameter for tce.by URLs

### 6. Setup Test Channel (Optional but Recommended)

To test the bot without sending notifications to your production channel:

1. **Create a test Telegram channel** or use the provided one (https://t.me/+rOY2zTmEcNo0ZGIy)
2. **Add your bot as an administrator** to the test channel
3. **Get the test channel Chat ID** using the helper script:
   ```bash
   # First, send a message to the test channel
   # Then run the helper script:
   python get_channel_id.py
   ```

   Or manually:
   ```bash
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   Look for the `chat` object with `type: "channel"` and copy the `id` value.

4. **Update your `.env` file** with test channel credentials:
   ```
   TEST_TELEGRAM_CHAT_ID=-1001234567890
   TEST_TELEGRAM_CHANNEL_USERNAME=@your_test_channel
   ```

Now you can use `--test-channel` flag to test without affecting your production channel!

## 🚀 Usage

### Basic Usage
```bash
# Monitor both sites (send to production channel)
python main.py

# Monitor only puppet-minsk.by
python main.py --puppet-only

# Monitor only tce.by
python main.py --tce-only

# Monitor tce.by with custom ID range
python main.py --tce-only --tce-start-id 4080 --tce-range 15
```

### Testing with Test Channel
```bash
# Send notifications to test channel instead of production
python main.py --test-channel

# Test only puppet-minsk.by monitoring in test channel
python main.py --puppet-only --test-channel

# Test only tce.by monitoring in test channel
python main.py --tce-only --test-channel

# Test with custom TCE ID range in test channel
python main.py --tce-only --tce-start-id 4080 --tce-range 5 --test-channel
```

**Note**: Test channel messages are prefixed with 🧪 [TEST] to distinguish them from production notifications.

### Command-Line Options
- `--puppet-only` - Monitor only puppet-minsk.by
- `--tce-only` - Monitor only tce.by
- `--tce-start-id ID` - Starting ID for TCE monitoring
- `--tce-range N` - Number of IDs to check for TCE
- `--test-channel` - Send notifications to test channel instead of production

### Testing
```bash
# Test channel connection and permissions
python test_channel_connection.py              # Test both channels
python test_channel_connection.py --test       # Test test channel only
python test_channel_connection.py --production # Test production channel only

# Get channel Chat ID
python get_channel_id.py

# Send a test notification (legacy)
python test_channel.py

# Test Telegram configuration (legacy)
python test_telegram.py
```

### Scheduled Execution with Cron

Create a wrapper script:
```bash
cat > run_monitor.sh << 'EOL'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 main.py >> cron_execution.log 2>&1
EOL

chmod +x run_monitor.sh
```

Add to crontab:
```bash
crontab -e
```

Add one of these lines:
```bash
# Run every 6 hours
0 */6 * * * /path/to/theater-monitor/run_monitor.sh

# Run twice daily (9 AM and 9 PM)
0 9,21 * * * /path/to/theater-monitor/run_monitor.sh

# Run once daily at 10 AM
0 10 * * * /path/to/theater-monitor/run_monitor.sh
```

## 🏛️ Architecture

### Components

- **main.py** - Main entry point, coordinates monitoring
- **theater_monitor.py** - Core monitoring logic for puppet-minsk.by
- **tce_monitor.py** - TCE.BY monitoring with Anubis bypass
- **performance_parser.py** - Resilient HTML parsing with fallback strategies
- **telegram_notifier.py** - Telegram notification handling
- **config.py** - Configuration management

### How It Works

1. **Puppet-Minsk Monitoring**:
   - Fetches the afisha page
   - Parses performances using multiple CSS selector strategies
   - Compares with previous data to find new performances

2. **TCE.BY Monitoring** (with Immediate Notifications):
   - Starts from base ID (last found event or configured start ID)
   - Checks next N IDs from base (default: 10 IDs ahead)
   - When event(s) found in range:
     - ✅ Sends immediate Telegram notification for each
     - ✅ Saves events to database
     - ✅ Updates base to highest found ID
     - ✅ Checks next N IDs from new base
   - Stops when no events found in N ID range
   - Uses Playwright/Selenium to bypass Anubis protection
   - **Smart date/time extraction:** Parses "Начало DD.MM.YYYY в HH:MM" format
   - Extracts event details with fallback parsing strategies
   - Tracks base ID (last found event) for next run
   - **Efficient:** Always checks 10 IDs ahead, no skipped IDs

3. **Resilient Parsing**:
   - Multiple CSS selector fallbacks
   - Structural HTML analysis when selectors fail
   - Pattern-based detection (dates, times, etc.)
   - Graceful handling of design changes

## 🔒 Anubis Protection Bypass

The monitor uses browser automation to bypass Anubis anti-bot protection on tce.by:

- **Playwright** (recommended): Modern, fast, more reliable
- **Selenium** (fallback): Traditional WebDriver approach
- **Requests** (last resort): May not work with Anubis active

The browser automation simulates a real user, waits for JavaScript challenges to complete, and extracts content.

## 📊 Data Storage

- `data/performances.json` - Cached performances from puppet-minsk.by
- `data/tce_events.json` - Cached events from tce.by
- `data/tce_last_id.json` - Last checked TCE event ID (auto-updated)
- `logs/theater_monitor.log` - Execution logs

## 🔔 Notification Behavior

### Puppet-Minsk.by
- **Batch notifications**: All new performances sent together at the end of the check

### TCE.BY
- **Immediate notifications**: Each event is sent as soon as it's discovered
- **Range-based scanning**: Always checks 10 IDs ahead of last found event
- **Smart continuation**: When event found, checks 10 more from that point
- **Automatic resume**: Next run starts from last found event

**Example TCE.BY flow:**
```
Base: 4070
Check IDs 4071-4080 (10 IDs from base)
  → Found events at 4073, 4075 ✅ Notify immediately for each
  → Highest: 4075

Base: 4075 (updated to highest found)
Check IDs 4076-4085 (10 IDs from new base)
  → Found event at 4082 ✅ Notify immediately
  → Highest: 4082

Base: 4082
Check IDs 4083-4092 (10 IDs from new base)
  → No events found ❌
  → Stop

Save base: 4082
Next run will check 4083-4092 again
```

This ensures no IDs are skipped and searching adapts to event distribution.

## 🐛 Troubleshooting

### Playwright Installation Issues
```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

### Selenium Issues
```bash
# Install Chrome/Chromium
# Ubuntu/Debian
sudo apt-get install chromium-browser

# Install ChromeDriver
# Download from: https://chromedriver.chromium.org/
```

### Anubis Still Blocking?
- Try running in non-headless mode: Set `USE_HEADLESS=false` in .env
- Increase browser timeout: Set `BROWSER_TIMEOUT=60` in .env
- Add delays between requests (modify `tce_monitor.py`)

### Design Changes Breaking Parser?
The parser has multiple fallback strategies, but if a site completely changes:
1. Check logs for parsing errors
2. Inspect the HTML structure
3. Add new selectors to the fallback arrays in `performance_parser.py` or `tce_monitor.py`

## 📄 License

Free to distribute under MIT License

## 🙏 Acknowledgements

- Vibe-coded with Claude for theater lovers
- Anubis bypass inspired by web archiving techniques