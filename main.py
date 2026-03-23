"""Main entry point for the theater monitoring script"""
import logging
import argparse
import sys
from tce_monitor import check_for_new_tce_events


def setup_logging():
    import config
    import os
    os.makedirs(config.LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(),
        ]
    )


def main():
    parser = argparse.ArgumentParser(description='Theater Performance Monitor')
    parser.add_argument('--test-channel', action='store_true',
                        help='Send notifications to test channel instead of production')
    parser.add_argument('--no-notify', action='store_true',
                        help='Collect and save events without sending Telegram notifications (use on first run to populate state)')
    args = parser.parse_args()

    setup_logging()
    logging.info("Starting theater performance monitor")

    try:
        new_events = check_for_new_tce_events(
            use_test_channel=args.test_channel,
            notify=not args.no_notify,
        )
        if new_events:
            suffix = " (notifications suppressed)" if args.no_notify else " and notified"
            logging.info(f"Completed: found {len(new_events)} new events{suffix}")
        else:
            logging.info("Completed: no new events")
    except Exception as e:
        logging.error(f"Error in main process: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
