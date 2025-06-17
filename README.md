# Theater Performance Monitor

App that monitors Belarusian State Puppet Theater theater websites for new performances and sends automated notifications via Telegram

## Theater Monitoring Bot

### ✨ Features
- 🔄 Automatically monitors theater website at configurable intervals
- 🔔 Sends notifications via Telegram when new performances are added
- 📱 Works with Telegram channels for public subscription
- 🪵 Comprehensive logging system for monitoring and debugging
- 💾 Persistent storage of performance data for reliable change detection
- 🚀 Designed for deployment on VPS servers with minimal resource usage

### 🔧 Requirements
- Python 3.6+
- pip packages:
  - requests
  - beautifulsoup4 
- Telegram bot token
- Linux/Unix system with cron (for scheduled execution)

### 🏗️ Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/igorekbs/theater-monitor.git
cd theater-monitor
```

#### 2. Use venv
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4
```

#### 3. Configure the Application
Copy .env.example to .env and edit with your settings


### 🚀 Usage

#### Manual Execution
```bash
# Run the monitor manually
python main.py

# Send a test notification
python test_channel.py

# Test Telegram configuration
python test_telegram.py
```

#### Scheduled Execution with Cron
Create a wrapper script:
```bash
cat > run_monitor.sh << 'EOL'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python main.py >> cron_execution.log 2>&1
EOL

chmod +x run_monitor.sh
```

Add to crontab:
```bash
crontab -e
```

Add the following line to run every 6 hours:

```
0 */6 * * * /path/to/theater-monitor/run_monitor.sh
```

### 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

### 🙏 Acknowledgements
- Vibe-coded with Claude for puppet theater lovers
