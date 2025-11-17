"""Main entry point for the theater monitoring script"""
import logging
import argparse
from theater_monitor import setup_logging, check_for_new_performances
from tce_monitor import check_for_new_tce_events
from telegram_notifier import notify_about_performances

def format_tce_events_as_performances(tce_events):
    """Convert TCE events to performance format for notifications"""
    performances = []
    for event in tce_events:
        performance = {
            'day': event.get('date', 'Unknown'),
            'time': event.get('time', 'Unknown'),
            'title': event.get('title', 'Unknown'),
            'image': event.get('image', ''),
            'image_alt': event.get('title', ''),
            'ticket_link': event.get('url', ''),
            'month_class': 'tce-event'
        }
        performances.append(performance)
    return performances

def main():
    """Main entry point for the theater monitoring script"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Theater Performance Monitor')
    parser.add_argument('--puppet-only', action='store_true',
                       help='Monitor only puppet-minsk.by')
    parser.add_argument('--tce-only', action='store_true',
                       help='Monitor only tce.by')
    parser.add_argument('--tce-start-id', type=int,
                       help='Starting ID for TCE monitoring')
    parser.add_argument('--tce-range', type=int,
                       help='Number of IDs to check for TCE')
    parser.add_argument('--test-channel', action='store_true',
                       help='Send notifications to test channel instead of production')

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    logging.info("Starting theater performance monitor")

    all_new_performances = []

    try:
        # Monitor puppet-minsk.by unless --tce-only is specified
        if not args.tce_only:
            logging.info("=" * 50)
            logging.info("Checking puppet-minsk.by for new performances")
            logging.info("=" * 50)
            try:
                new_performances = check_for_new_performances()
                if new_performances:
                    logging.info(f"Found {len(new_performances)} new performances on puppet-minsk.by")
                    all_new_performances.extend(new_performances)
                else:
                    logging.info("No new performances found on puppet-minsk.by")
            except Exception as e:
                logging.error(f"Error checking puppet-minsk.by: {e}")

        # Monitor tce.by unless --puppet-only is specified
        if not args.puppet_only:
            logging.info("=" * 50)
            logging.info("Checking tce.by for new events (with IMMEDIATE notifications)")
            logging.info("=" * 50)
            try:
                # Import here to avoid issues if playwright/selenium not installed
                from tce_monitor import check_for_new_tce_events

                # TCE events are sent immediately, so we pass the test channel flag
                new_tce_events = check_for_new_tce_events(use_test_channel=args.test_channel)
                if new_tce_events:
                    logging.info(f"Found {len(new_tce_events)} new events on tce.by (already notified)")
                    # Note: TCE events are NOT added to batch notifications
                    # They were already sent immediately as they were found
                else:
                    logging.info("No new events found on tce.by")
            except ImportError as e:
                logging.error(f"TCE monitoring requires playwright or selenium: {e}")
                logging.info("Install with: pip install playwright && playwright install chromium")
                logging.info("Or: pip install selenium")
            except Exception as e:
                logging.error(f"Error checking tce.by: {e}")

        # Send batch notification for puppet-minsk performances (TCE events already sent)
        if all_new_performances:
            logging.info("=" * 50)
            channel_type = "test" if args.test_channel else "production"
            logging.info(f"Puppet-Minsk: Found {len(all_new_performances)} new performances, sending batch notification to {channel_type} channel")
            logging.info("=" * 50)
            notification_sent = notify_about_performances(all_new_performances, use_test_channel=args.test_channel)
            if notification_sent:
                logging.info(f"Puppet-Minsk notification sent successfully to {channel_type} channel")
            else:
                logging.error("Failed to send Puppet-Minsk notification")
        else:
            if not args.tce_only:  # Only log this if we checked puppet-minsk
                logging.info("=" * 50)
                logging.info("No new puppet-minsk performances found")
                logging.info("=" * 50)

        logging.info("Theater monitoring completed successfully")

    except Exception as e:
        logging.error(f"Error in main process: {e}")

if __name__ == "__main__":
    main()