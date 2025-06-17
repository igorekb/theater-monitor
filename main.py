"""Main entry point for the theater monitoring script"""
import logging
from theater_monitor import setup_logging, check_for_new_performances
from telegram_notifier import notify_about_performances

def main():
    """Main entry point for the theater monitoring script"""
    # Setup logging
    setup_logging()
    
    logging.info("Starting theater performance monitor")
    
    try:
        # Check for new performances
        new_performances = check_for_new_performances()
        
        # Only send notification if new performances are found
        if new_performances:
            logging.info(f"Found {len(new_performances)} new performances, sending notification")
            notification_sent = notify_about_performances(new_performances)
            if notification_sent:
                logging.info("Telegram notification sent successfully")
            else:
                logging.error("Failed to send Telegram notification")
        else:
            logging.info("No new performances found, no notification needed")
            
        logging.info("Theater monitoring completed successfully")
        
    except Exception as e:
        logging.error(f"Error in main process: {e}")

if __name__ == "__main__":
    main()