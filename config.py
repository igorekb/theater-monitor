import os
from dotenv import load_dotenv

# Base dirs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_DIR = os.path.join(BASE_DIR, 'logs')


TCE_DATA_FILE = os.path.join(DATA_DIR, 'tce_events.json')
TCE_PROCESSED_IDS_FILE = os.path.join(DATA_DIR, 'tce_processed_ids.json')
LOG_FILE = os.path.join(LOG_DIR, 'theater_monitor.log')

# TCE.BY monitoring configuration
TCE_BASE_URL = "https://tce.by/shows.html"
TCE_BASE_PARAM = "RkZDMTE2MUQtMTNFNy00NUIyLTg0QzYtMURDMjRBNTc1ODA0"
TCE_SEARCH_API_URL = "https://tce.by/index.php?view=shows&action=find&kind=text"
TCE_MONTHS_AHEAD = 4  # current month + 3 future months per run

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

# Shared HTTP fingerprint constants — keep in sync with actual Chrome release
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Safari/537.36"
)
ACCEPT_LANGUAGE = "ru-RU,ru;q=0.9,be;q=0.8,en-US;q=0.7,en;q=0.6"