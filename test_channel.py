import requests
import sys
import config
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_channel_post():
    """Test posting to the Telegram channel"""
    print(f"Testing post to channel {config.TELEGRAM_CHAT_ID}")
    
    bot_token = config.TELEGRAM_BOT_TOKEN
    channel_id = config.TELEGRAM_CHAT_ID
    
    if not bot_token or not channel_id:
        print("❌ Error: Bot token or channel ID not configured")
        return False
    
    test_time = time.strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🎭 <b>Theater Channel Test</b>

This is a test message posted to the channel.
Time: {test_time}

If this message appears in your channel, the configuration is working correctly!
"""
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        response = requests.post(
            url, 
            json={
                'chat_id': channel_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_notification': False
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Success! Test message posted to channel.")
            print(f"Check your channel to confirm: {config.TELEGRAM_CHANNEL_USERNAME}")
            return True
        else:
            print(f"❌ Failed to post message. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_channel_post()
    sys.exit(0 if success else 1)