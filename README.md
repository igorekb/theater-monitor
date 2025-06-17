# Theater Monitor

App that monitors Puppet Theater website for new performances and remind about new performances in Telegram

### 🔧 Requirements
- Python 3.6+
- pip:
  - requests
  - beautifulsoup4
  - dotenv 
- Telegram bot token
- Telegram channel
- Linux VPS with cron 

### 🏗️ Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/igorekbs/theater-monitor.git
cd theater-monitor
```

#### 2. Create venv and install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4 dotenv
```

#### 3. Configure
Copy .env.example to .env and add your settings


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
python3 main.py >> cron_execution.log 2>&1
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
Free to distibute under MIT License

### 🙏 Acknowledgements
- Vibe-coded with Claude for puppet theater lovers