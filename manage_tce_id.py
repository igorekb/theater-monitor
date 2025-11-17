#!/usr/bin/env python3
"""Helper script to manage TCE last checked ID"""
import json
import os
import sys
import argparse
import config

def show_last_id():
    """Display the current last checked ID"""
    if os.path.exists(config.TCE_LAST_ID_FILE):
        try:
            with open(config.TCE_LAST_ID_FILE, 'r') as f:
                data = json.load(f)
                last_id = data.get('last_checked_id', 'Not set')
                print(f"📊 Current last checked TCE ID: {last_id}")
                print(f"📂 File location: {config.TCE_LAST_ID_FILE}")
                return last_id
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None
    else:
        print(f"⚠️  No last checked ID file found")
        print(f"   Default will be used: {config.TCE_START_ID}")
        print(f"   File will be created at: {config.TCE_LAST_ID_FILE}")
        return None


def set_last_id(new_id):
    """Set the last checked ID to a specific value"""
    try:
        os.makedirs(os.path.dirname(config.TCE_LAST_ID_FILE), exist_ok=True)
        with open(config.TCE_LAST_ID_FILE, 'w') as f:
            json.dump({'last_checked_id': new_id}, f, indent=2)
        print(f"✅ Last checked ID set to: {new_id}")
        print(f"📂 Saved to: {config.TCE_LAST_ID_FILE}")
        print(f"\nNext run will start checking from ID {new_id}")
    except Exception as e:
        print(f"❌ Error setting ID: {e}")


def reset_to_default():
    """Reset to the default start ID from config"""
    set_last_id(config.TCE_START_ID)
    print(f"🔄 Reset to default start ID from config.py")


def delete_file():
    """Delete the last checked ID file"""
    if os.path.exists(config.TCE_LAST_ID_FILE):
        try:
            os.remove(config.TCE_LAST_ID_FILE)
            print(f"✅ Deleted last checked ID file")
            print(f"   Next run will use default: {config.TCE_START_ID}")
        except Exception as e:
            print(f"❌ Error deleting file: {e}")
    else:
        print(f"⚠️  File doesn't exist, nothing to delete")


def main():
    parser = argparse.ArgumentParser(
        description='Manage TCE last checked ID',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_tce_id.py                 # Show current ID
  python manage_tce_id.py --show          # Show current ID
  python manage_tce_id.py --set 4080      # Set ID to 4080
  python manage_tce_id.py --reset         # Reset to default from config
  python manage_tce_id.py --delete        # Delete tracking file

Understanding TCE ID tracking:
- The monitor remembers the last checked ID between runs
- When an event is found, checking continues from next ID
- After N consecutive 404s (default: 10), checking stops
- Next run resumes from where the last run stopped
- This prevents duplicate checks and ensures continuous monitoring
        """
    )

    parser.add_argument('--show', action='store_true',
                       help='Show current last checked ID')
    parser.add_argument('--set', type=int, metavar='ID',
                       help='Set last checked ID to specific value')
    parser.add_argument('--reset', action='store_true',
                       help='Reset to default start ID from config')
    parser.add_argument('--delete', action='store_true',
                       help='Delete the last checked ID file')

    args = parser.parse_args()

    print("=" * 70)
    print("TCE Last Checked ID Manager")
    print("=" * 70)
    print()

    if args.set:
        set_last_id(args.set)
    elif args.reset:
        reset_to_default()
    elif args.delete:
        delete_file()
    else:
        # Default action: show current ID
        show_last_id()

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
