#!/usr/bin/env python3
"""Diagnostic script to test Telegram channel connection"""
import requests
import sys
import os
import argparse
from dotenv import load_dotenv

load_dotenv()

def test_bot_token(bot_token):
    """Test if bot token is valid"""
    print("\n" + "=" * 70)
    print("1. Testing Bot Token")
    print("=" * 70)

    url = f"https://api.telegram.org/bot{bot_token}/getMe"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get('ok'):
            bot_info = data.get('result', {})
            print(f"✅ Bot token is VALID")
            print(f"   Bot name: {bot_info.get('first_name')}")
            print(f"   Bot username: @{bot_info.get('username')}")
            print(f"   Bot ID: {bot_info.get('id')}")
            return True
        else:
            print(f"❌ Bot token is INVALID")
            print(f"   Error: {data.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Error testing bot token: {e}")
        return False


def test_channel_access(bot_token, chat_id, channel_name):
    """Test if bot can access the channel"""
    print("\n" + "=" * 70)
    print(f"2. Testing {channel_name} Channel Access")
    print("=" * 70)
    print(f"   Chat ID: {chat_id}")

    # First, try to get chat info
    url = f"https://api.telegram.org/bot{bot_token}/getChat"

    try:
        response = requests.post(url, json={'chat_id': chat_id}, timeout=10)
        data = response.json()

        if data.get('ok'):
            chat_info = data.get('result', {})
            print(f"✅ Bot has access to the channel")
            print(f"   Channel title: {chat_info.get('title', 'N/A')}")
            print(f"   Channel username: @{chat_info.get('username', 'N/A')}")
            print(f"   Channel type: {chat_info.get('type', 'N/A')}")

            # Check bot permissions
            check_bot_permissions(bot_token, chat_id, channel_name)
            return True
        else:
            print(f"❌ Bot CANNOT access the channel")
            print(f"   Error: {data.get('description')}")
            print(f"\n   Possible issues:")
            print(f"   - Bot is not added to the channel")
            print(f"   - Chat ID is incorrect")
            print(f"   - Bot was removed from the channel")
            return False
    except Exception as e:
        print(f"❌ Error testing channel access: {e}")
        return False


def check_bot_permissions(bot_token, chat_id, channel_name):
    """Check bot permissions in the channel"""
    print(f"\n   Checking {channel_name} bot permissions...")

    url = f"https://api.telegram.org/bot{bot_token}/getChatMember"

    try:
        # Get the bot's own ID first
        me_response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10)
        me_data = me_response.json()
        bot_id = me_data.get('result', {}).get('id')

        # Check bot's permissions
        response = requests.post(url, json={'chat_id': chat_id, 'user_id': bot_id}, timeout=10)
        data = response.json()

        if data.get('ok'):
            member_info = data.get('result', {})
            status = member_info.get('status')
            print(f"   Bot status: {status}")

            if status == 'administrator':
                print(f"   ✅ Bot is an administrator")

                # Check specific permissions
                can_post = member_info.get('can_post_messages', False)
                can_edit = member_info.get('can_edit_messages', False)

                if can_post:
                    print(f"   ✅ Bot CAN post messages")
                else:
                    print(f"   ❌ Bot CANNOT post messages - THIS IS THE PROBLEM!")
                    print(f"      → Add 'Post messages' permission to the bot")

                if can_edit:
                    print(f"   ✅ Bot CAN edit messages")

            elif status == 'member':
                print(f"   ⚠️  Bot is only a member, not an administrator")
                print(f"      → Make the bot an administrator with 'Post messages' permission")
            else:
                print(f"   ❌ Bot has insufficient permissions")
        else:
            print(f"   ❌ Could not check permissions: {data.get('description')}")

    except Exception as e:
        print(f"   ⚠️  Could not check permissions: {e}")


def test_send_message(bot_token, chat_id, channel_name):
    """Try to send a test message"""
    print("\n" + "=" * 70)
    print(f"3. Testing Message Send to {channel_name}")
    print("=" * 70)

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    test_message = f"🧪 Test message from theater-monitor\n\nThis is a test to verify bot permissions.\n\nTime: {os.popen('date').read().strip()}"

    try:
        payload = {
            'chat_id': chat_id,
            'text': test_message,
            'disable_notification': True
        }

        response = requests.post(url, json=payload, timeout=10)
        data = response.json()

        if data.get('ok'):
            print(f"✅ Test message sent SUCCESSFULLY!")
            print(f"   Message ID: {data.get('result', {}).get('message_id')}")
            return True
        else:
            print(f"❌ Failed to send test message")
            print(f"   Error: {data.get('description')}")
            error_code = data.get('error_code')

            if error_code == 400:
                print(f"\n   Common 400 errors:")
                print(f"   - Chat ID is invalid or incorrect")
                print(f"   - Bot was removed from the channel")
            elif error_code == 403:
                print(f"\n   This is a permissions error:")
                print(f"   - Bot needs to be an administrator")
                print(f"   - Bot needs 'Post messages' permission")

            return False
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        return False


def main():
    """Main diagnostic function"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Test Telegram channel connection and permissions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_channel_connection.py              # Test both channels
  python test_channel_connection.py --production # Test production channel only
  python test_channel_connection.py --test       # Test test channel only
        """
    )
    parser.add_argument('--production', action='store_true',
                       help='Test production channel only')
    parser.add_argument('--test', action='store_true',
                       help='Test test channel only')

    args = parser.parse_args()

    # Determine what to test
    test_production = True
    test_test = True

    if args.production and not args.test:
        test_test = False
    elif args.test and not args.production:
        test_production = False

    print("=" * 70)
    print("Telegram Channel Connection Diagnostic")
    print("=" * 70)

    if test_production and test_test:
        print("Mode: Testing BOTH channels")
    elif test_production:
        print("Mode: Testing PRODUCTION channel only")
    elif test_test:
        print("Mode: Testing TEST channel only")

    # Load configuration
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    prod_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    test_chat_id = os.getenv('TEST_TELEGRAM_CHAT_ID')

    if not bot_token or bot_token == 'default_dev_token':
        print("\n❌ ERROR: TELEGRAM_BOT_TOKEN not found or not set in .env file")
        print("   Please add your bot token to the .env file")
        sys.exit(1)

    print(f"\nBot token found: {bot_token[:10]}...{bot_token[-5:]}")

    if test_production:
        print(f"Production Chat ID: {prod_chat_id}")
    if test_test:
        print(f"Test Chat ID: {test_chat_id}")

    # Test bot token
    if not test_bot_token(bot_token):
        print("\n❌ Cannot continue - bot token is invalid")
        sys.exit(1)

    results = []

    # Test production channel if requested and configured
    if test_production:
        if prod_chat_id and prod_chat_id != 'default_dev_chat_id':
            prod_access = test_channel_access(bot_token, prod_chat_id, "Production")
            if prod_access:
                prod_send = test_send_message(bot_token, prod_chat_id, "Production")
                results.append(("Production", prod_send))
            else:
                results.append(("Production", False))
        else:
            print("\n" + "=" * 70)
            print("⚠️  Production channel not configured")
            print("=" * 70)
            print("TELEGRAM_CHAT_ID is not set in .env file")

    # Test test channel if requested and configured
    if test_test:
        if test_chat_id and test_chat_id not in ['default_test_chat_id', 'REPLACE_WITH_TEST_CHANNEL_ID']:
            test_access = test_channel_access(bot_token, test_chat_id, "Test")
            if test_access:
                test_send = test_send_message(bot_token, test_chat_id, "Test")
                results.append(("Test", test_send))
            else:
                results.append(("Test", False))
        else:
            print("\n" + "=" * 70)
            print("⚠️  Test channel not configured")
            print("=" * 70)
            print("To configure test channel:")
            print("1. Add bot to test channel as administrator")
            print("2. Run: python get_channel_id.py")
            print("3. Add TEST_TELEGRAM_CHAT_ID to .env file")
            print("\nCurrent value: " + str(test_chat_id))

    # Summary
    print("\n" + "=" * 70)
    print("Diagnostic Complete - SUMMARY")
    print("=" * 70)

    if results:
        all_passed = all(result[1] for result in results)
        for channel_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{channel_name} Channel: {status}")

        if all_passed:
            print("\n🎉 All tests PASSED! You're ready to use the monitor.")
        else:
            print("\n⚠️  Some tests FAILED. Please fix the issues above.")
    else:
        print("No channels were tested. Please configure channels in .env file.")


if __name__ == "__main__":
    main()
