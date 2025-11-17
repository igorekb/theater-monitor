import os
from dotenv import load_dotenv

# Base dirs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_DIR = os.path.join(BASE_DIR, 'logs')


DATA_FILE = os.path.join(DATA_DIR, 'performances.json')
TCE_DATA_FILE = os.path.join(DATA_DIR, 'tce_events.json')
TCE_LAST_ID_FILE = os.path.join(DATA_DIR, 'tce_last_id.json')
LOG_FILE = os.path.join(LOG_DIR, 'theater_monitor.log')


THEATER_URL = "https://puppet-minsk.by/afisha"

# TCE.BY ID-based monitoring configuration
TCE_BASE_URL = "https://tce.by/shows.html"
TCE_BASE_PARAM = "RkZDMTE2MUQtMTNFNy00NUIyLTg0QzYtMURDMjRBNTc1ODA0"
TCE_START_ID = 4070
TCE_ID_RANGE = 10  # Check next 10 IDs

load_dotenv()

# Production Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'default_dev_token')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'default_dev_chat_id')
TELEGRAM_CHANNEL_USERNAME = os.getenv('TELEGRAM_CHANNEL_USERNAME', 'default_dev_username')

# Test Telegram channel settings
TEST_TELEGRAM_CHAT_ID = os.getenv('TEST_TELEGRAM_CHAT_ID', 'default_test_chat_id')
TEST_TELEGRAM_CHANNEL_USERNAME = os.getenv('TEST_TELEGRAM_CHANNEL_USERNAME', 'default_test_username')

# Browser automation settings for Anubis bypass
USE_HEADLESS = os.getenv('USE_HEADLESS', 'true').lower() == 'true'
BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', '30'))