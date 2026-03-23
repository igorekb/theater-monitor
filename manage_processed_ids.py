#!/usr/bin/env python3
"""Utility to view or clear the processed TCE event IDs state.

Usage:
  python manage_processed_ids.py --show     # print count and all IDs
  python manage_processed_ids.py --clear    # delete state file (next run re-notifies all)
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def show():
    if not os.path.exists(config.TCE_PROCESSED_IDS_FILE):
        print(f"State file not found: {config.TCE_PROCESSED_IDS_FILE}")
        return
    with open(config.TCE_PROCESSED_IDS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    ids = data.get('processed_ids', [])
    print(f"Processed event IDs: {len(ids)}")
    print(f"File: {config.TCE_PROCESSED_IDS_FILE}")
    if ids:
        print(f"ID range: {min(ids)} – {max(ids)}")
        print(f"IDs: {ids}")


def clear():
    if not os.path.exists(config.TCE_PROCESSED_IDS_FILE):
        print("State file does not exist, nothing to clear.")
        return
    os.remove(config.TCE_PROCESSED_IDS_FILE)
    print(f"Deleted {config.TCE_PROCESSED_IDS_FILE}")
    print("Next run will re-notify all current events.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage TCE processed event IDs')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--show', action='store_true', help='Show current state')
    group.add_argument('--clear', action='store_true', help='Delete state file')
    args = parser.parse_args()

    if args.show:
        show()
    elif args.clear:
        clear()
