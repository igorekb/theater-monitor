#!/usr/bin/env python3
"""Helper script to get Telegram channel Chat ID"""
import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def get_channel_id():
    """Fetch and display channel information from Telegram"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not bot_token or bot_token == 'default_dev_token':
        print("Error: TELEGRAM_BOT_TOKEN not found in .env file")
        print("Please add your bot token to the .env file first")
        sys.exit(1)

    print(f"Using bot token: {bot_token[:10]}...")
    print("\nFetching updates from Telegram...")

    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get('ok'):
            print(f"Error: {data.get('description', 'Unknown error')}")
            sys.exit(1)

        results = data.get('result', [])

        if not results:
            print("\nNo updates found!")
            print("\nTo get your channel ID:")
            print("1. Send a message to your channel")
            print("2. Run this script again within a few minutes")
            sys.exit(0)

        print(f"\nFound {len(results)} updates\n")
        print("=" * 70)

        channels_found = False

        for update in results:
            # Check for channel posts
            if 'channel_post' in update:
                post = update['channel_post']
                chat = post.get('chat', {})

                if chat.get('type') == 'channel':
                    channels_found = True
                    print(f"\n📢 Channel: {chat.get('title', 'Unknown')}")
                    print(f"   Chat ID: {chat.get('id')}")
                    print(f"   Username: @{chat.get('username', 'N/A')}")
                    print(f"   Type: {chat.get('type')}")
                    print("-" * 70)

        if not channels_found:
            print("\nNo channel posts found in recent updates.")
            print("\nTo get your channel ID:")
            print("1. Make sure your bot is added as an administrator to the channel")
            print("2. Send a message to the channel")
            print("3. Run this script again")
        else:
            print("\n✅ Copy the Chat ID above and add it to your .env file:")
            print("   TEST_TELEGRAM_CHAT_ID=<the_chat_id_here>")
            print("   TEST_TELEGRAM_CHANNEL_USERNAME=@<username_here>")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching updates: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 70)
    print("Telegram Channel ID Finder")
    print("=" * 70)
    get_channel_id()
