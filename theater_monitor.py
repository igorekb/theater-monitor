"""Core functionality for monitoring theater performances"""
import json
import os
import logging
import time
from datetime import datetime
from performance_parser import fetch_page, parse_performances
import config

def ensure_directory_exists(directory_path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logging.info(f"Created directory: {directory_path}")

def setup_logging():
    """Set up logging configuration"""
    # Create logs directory if it doesn't exist
    ensure_directory_exists(os.path.dirname(config.LOG_FILE))
    
    logging.basicConfig(
        filename=config.LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def load_previous_data():
    """Load previously saved performance data"""
    # Ensure data directory exists
    ensure_directory_exists(os.path.dirname(config.DATA_FILE))
    
    if os.path.exists(config.DATA_FILE):
        try:
            with open(config.DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logging.info(f"Successfully loaded {len(data)} performances from {config.DATA_FILE}")
                return data
        except Exception as e:
            logging.error(f"Error loading previous data: {e}")
            # Create backup of corrupted file if it exists
            if os.path.getsize(config.DATA_FILE) > 0:
                # Create backups directory if it doesn't exist
                backup_dir = os.path.join(os.path.dirname(config.DATA_FILE), 'backups')
                ensure_directory_exists(backup_dir)
                
                backup_file = os.path.join(backup_dir, f"data_backup_{int(time.time())}.json")
                try:
                    # Copy the file instead of renaming to preserve the original
                    with open(config.DATA_FILE, 'r', encoding='utf-8') as src:
                        with open(backup_file, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                    logging.info(f"Created backup of corrupted data file: {backup_file}")
                except Exception as be:
                    logging.error(f"Failed to create backup of corrupted file: {be}")
            return []
    logging.info(f"No previous data file ({config.DATA_FILE}) exists")
    return []

def save_current_data(performances):
    """Save current performance data"""
    # Ensure data directory exists
    ensure_directory_exists(os.path.dirname(config.DATA_FILE))
    
    try:
        with open(config.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(performances, f, ensure_ascii=False, indent=2)
        logging.info(f"Successfully saved {len(performances)} performances to {config.DATA_FILE}")
    except Exception as e:
        logging.error(f"Error saving current data: {e}")

def compare_data(old_data, new_data):
    """Compare old and new data to find changes"""
    # Create sets of performance signatures for comparison
    old_signatures = {(p['title'], p['day'], p['time']) for p in old_data}
    new_signatures = {(p['title'], p['day'], p['time']) for p in new_data}
    
    # Find new performances
    new_performances = new_signatures - old_signatures
    
    # Get full details of new performances
    new_performance_details = [
        p for p in new_data 
        if (p['title'], p['day'], p['time']) in new_performances
    ]
    
    logging.info(f"Found {len(new_performance_details)} new performances")
    return new_performance_details

def check_for_new_performances():
    """Check for new performances and return any that are found"""
    try:
        # Fetch current page
        html = fetch_page(config.THEATER_URL)
        
        # Parse performances
        current_performances = parse_performances(html)
        logging.info(f"Found {len(current_performances)} total performances on the website")
        
        # Load previous data
        previous_performances = load_previous_data()
        logging.info(f"Loaded {len(previous_performances)} performances from previous check")
        
        # Compare to find new performances
        new_performances = compare_data(previous_performances, current_performances)
        
        # Save current data for future comparison (whether or not we found new performances)
        save_current_data(current_performances)
        logging.info("Current performance data saved for future comparison")
            
        return new_performances
        
    except Exception as e:
        error_msg = f"Unexpected error in performance check: {e}"
        logging.error(error_msg)
        return []