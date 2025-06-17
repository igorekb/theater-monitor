import requests
import time
import sys

# Import settings from config
try:
    import config
    BOT_TOKEN = getattr(config, 'TELEGRAM_BOT_TOKEN', None)
    CHAT_ID = getattr(config, 'TELEGRAM_CHAT_ID', None)
except ImportError:
    print("❌ Error: config.py file not found or has errors.")
    BOT_TOKEN = None
    CHAT_ID = None

def test_telegram_bot(bot_token=None, chat_id=None, verbose=True):
    """
    Test sending a message through the Telegram bot
    
    Args:
        bot_token: Optional override for bot token
        chat_id: Optional override for chat ID
        verbose: Whether to print status messages
    
    Returns:
        bool: Success status
    """
    if verbose:
        print("=== Telegram Bot Message Test ===")
    
    # Use provided values or fall back to config, or prompt if needed
    bot_token = bot_token or BOT_TOKEN
    chat_id = chat_id or CHAT_ID
    
    # Handle missing credentials
    if not bot_token:
        bot_token = input("Bot token not found in config. Enter your bot token: ")
    if not chat_id:
        chat_id = input("Chat ID not found in config. Enter your chat ID: ")
    
    if verbose:
        print("\nConfiguration:")
        print(f"- Bot Token: {bot_token[:5]}...{bot_token[-5:] if bot_token else 'None'}")
        print(f"- Chat ID: {chat_id}")
        print("\nSending test message...")
    
    test_time = time.strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""
🎭 <b>Theater Monitoring Bot - Test Message</b>

This is a test message from your Theater Monitoring Bot.
Time: {test_time}

If you can see this message, your bot is configured correctly!
"""
    
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            if verbose:
                print("✅ Success! Test message sent.")
                print("Check your Telegram to confirm you received the message.")
            return True
        else:
            if verbose:
                print(f"❌ Failed to send message. Status code: {response.status_code}")
                print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        if verbose:
            print(f"❌ Error: {e}")
        return False

def show_help():
    """Display help information"""
    print("""
Usage: python test_telegram.py [OPTIONS]

Test the Telegram notification functionality using your config.py settings.

Options:
  --help      Show this help message
  --silent    Run without verbose output
  --token=X   Override the bot token from config.py
  --chat=X    Override the chat ID from config.py

Examples:
  python test_telegram.py
  python test_telegram.py --silent
  python test_telegram.py --token=123456789:ABCdef... --chat=123456789
""")

if __name__ == "__main__":
    # Process command line arguments
    verbose = True
    custom_token = None
    custom_chat_id = None
    
    for arg in sys.argv[1:]:
        if arg == "--help":
            show_help()
            sys.exit(0)
        elif arg == "--silent":
            verbose = False
        elif arg.startswith("--token="):
            custom_token = arg.split("=", 1)[1]
        elif arg.startswith("--chat="):
            custom_chat_id = arg.split("=", 1)[1]
    
    # Print configuration status
    if verbose:
        if not BOT_TOKEN:
            print("⚠️  Warning: TELEGRAM_BOT_TOKEN not found in config.py")
        if not CHAT_ID:
            print("⚠️  Warning: TELEGRAM_CHAT_ID not found in config.py")
    
    # Run the test
    success = test_telegram_bot(custom_token, custom_chat_id, verbose)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)