import os
from dotenv import load_dotenv

# Base dirs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_DIR = os.path.join(BASE_DIR, 'logs')


DATA_FILE = os.path.join(DATA_DIR, 'performances.json')
LOG_FILE = os.path.join(LOG_DIR, 'theater_monitor.log')


THEATER_URL = "https://puppet-minsk.by/afisha"

load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'default_dev_token')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'default_dev_chat_id')
TELEGRAM_CHANNEL_USERNAME = os.getenv('TELEGRAM_CHANNEL_USERNAME', 'default_dev_username')