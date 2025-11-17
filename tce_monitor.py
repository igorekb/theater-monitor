"""Module for monitoring TCE.BY events with ID-based checking and Anubis bypass"""
import json
import os
import logging
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
import config

# Try to import playwright, fallback to selenium if not available
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    BROWSER_ENGINE = 'playwright'
except ImportError:
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        BROWSER_ENGINE = 'selenium'
    except ImportError:
        BROWSER_ENGINE = None
        logging.warning("Neither Playwright nor Selenium found. TCE monitoring will use requests (may fail with Anubis)")


def fetch_tce_page_with_playwright(url, wait_time=5):
    """Fetch page using Playwright to bypass Anubis protection"""
    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(
                headless=config.USE_HEADLESS,
                args=['--disable-blink-features=AutomationControlled']
            )

            # Create context with realistic headers
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US'
            )

            # Open page
            page = context.new_page()

            # Navigate to URL
            logging.info(f"Fetching TCE page: {url}")
            page.goto(url, wait_until='networkidle', timeout=config.BROWSER_TIMEOUT * 1000)

            # Wait for content to load (Anubis challenge to complete)
            time.sleep(wait_time)

            # Get page content
            content = page.content()

            # Close browser
            browser.close()

            return content

    except PlaywrightTimeout as e:
        logging.error(f"Playwright timeout: {e}")
        raise
    except Exception as e:
        logging.error(f"Error fetching page with Playwright: {e}")
        raise


def fetch_tce_page_with_selenium(url, wait_time=5):
    """Fetch page using Selenium to bypass Anubis protection"""
    try:
        # Set up Chrome options
        chrome_options = Options()
        if config.USE_HEADLESS:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)

        try:
            # Navigate to URL
            logging.info(f"Fetching TCE page: {url}")
            driver.get(url)

            # Wait for content to load (Anubis challenge to complete)
            time.sleep(wait_time)

            # Get page content
            content = driver.page_source

            return content

        finally:
            driver.quit()

    except TimeoutException as e:
        logging.error(f"Selenium timeout: {e}")
        raise
    except Exception as e:
        logging.error(f"Error fetching page with Selenium: {e}")
        raise


def fetch_tce_page_with_requests(url):
    """Fallback: Fetch page using requests (may not work with Anubis)"""
    import requests

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        logging.info(f"Fetching TCE page with requests: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        logging.error(f"Error fetching page with requests: {e}")
        raise


def fetch_tce_page(url):
    """Fetch TCE page using available browser automation tool"""
    if BROWSER_ENGINE == 'playwright':
        return fetch_tce_page_with_playwright(url)
    elif BROWSER_ENGINE == 'selenium':
        return fetch_tce_page_with_selenium(url)
    else:
        logging.warning("Using requests fallback - may not work with Anubis protection")
        return fetch_tce_page_with_requests(url)


def extract_date_time_from_text(text):
    """
    Extract date and time from Russian text like "Начало 07.01.2026 в 15:45"

    Returns:
        tuple: (date_str, time_str) or (None, None) if not found
    """
    # Pattern: "Начало DD.MM.YYYY в HH:MM"
    pattern = r'Начало\s+(\d{2})\.(\d{2})\.(\d{4})\s+в\s+(\d{2}):(\d{2})'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        day, month, year, hour, minute = match.groups()
        date_str = f"{day}.{month}.{year}"
        time_str = f"{hour}:{minute}"
        return date_str, time_str

    # Alternative pattern: just date "DD.MM.YYYY"
    pattern_date_only = r'(\d{2})\.(\d{2})\.(\d{4})'
    match_date = re.search(pattern_date_only, text)

    if match_date:
        day, month, year = match_date.groups()
        date_str = f"{day}.{month}.{year}"

        # Try to find time separately "HH:MM"
        pattern_time = r'(\d{2}):(\d{2})'
        match_time = re.search(pattern_time, text)
        if match_time:
            hour, minute = match_time.groups()
            time_str = f"{hour}:{minute}"
            return date_str, time_str

        return date_str, None

    return None, None


def parse_tce_event(html, event_id, url):
    """Parse event information from TCE page with multiple fallback strategies"""
    soup = BeautifulSoup(html, 'html.parser')

    event = {
        'id': event_id,
        'url': url,
        'title': 'Unknown',
        'date': 'Unknown',
        'time': 'Unknown',
        'venue': 'Unknown',
        'description': '',
        'image': '',
        'found_at': datetime.now().isoformat()
    }

    try:
        # Check if page exists (not 404 or error page)
        # Strategy 1: Look for common error indicators
        error_indicators = [
            'страница не найдена',
            'page not found',
            '404',
            'ошибка'
        ]

        page_text = soup.get_text().lower()
        if any(indicator in page_text for indicator in error_indicators):
            logging.info(f"Event ID {event_id} appears to be a 404 or error page")
            return None

        # Get full page text for date/time extraction
        full_text = soup.get_text()

        # Strategy 2: Multiple selector attempts for title
        title_selectors = [
            ('h1', {}),
            ('h1', {'class': 'title'}),
            ('h1', {'class': 'event-title'}),
            ('div', {'class': 'title'}),
            ('.show-title', {}),
            ('.event-name', {}),
        ]

        for selector, attrs in title_selectors:
            if selector.startswith('.'):
                element = soup.select_one(selector)
            else:
                element = soup.find(selector, attrs if attrs else None)

            if element and element.text.strip():
                event['title'] = element.text.strip()
                logging.info(f"Found title using selector {selector}: {event['title']}")
                break

        # Strategy 3: Extract date and time from "Начало DD.MM.YYYY в HH:MM" pattern
        date_str, time_str = extract_date_time_from_text(full_text)

        if date_str:
            event['date'] = date_str
            logging.info(f"Extracted date from text: {date_str}")

        if time_str:
            event['time'] = time_str
            logging.info(f"Extracted time from text: {time_str}")

        # Strategy 4: Fallback to selector-based date/time if not found in text
        if event['date'] == 'Unknown':
            date_selectors = [
                ('div', {'class': 'date'}),
                ('span', {'class': 'date'}),
                ('time', {}),
                ('.event-date', {}),
                ('.show-date', {}),
            ]

            for selector, attrs in date_selectors:
                if selector.startswith('.'):
                    element = soup.select_one(selector)
                else:
                    element = soup.find(selector, attrs if attrs else None)

                if element and element.text.strip():
                    event['date'] = element.text.strip()
                    break

        # Strategy 4: Look for venue information
        venue_selectors = [
            ('div', {'class': 'venue'}),
            ('span', {'class': 'venue'}),
            ('.event-venue', {}),
            ('.location', {}),
        ]

        for selector, attrs in venue_selectors:
            if selector.startswith('.'):
                element = soup.select_one(selector)
            else:
                element = soup.find(selector, attrs if attrs else None)

            if element and element.text.strip():
                event['venue'] = element.text.strip()
                break

        # Strategy 5: Extract image
        img = soup.find('img', {'alt': True})
        if not img:
            img = soup.find('img')

        if img and img.get('src'):
            event['image'] = img['src']
            if not event['image'].startswith(('http://', 'https://')):
                event['image'] = f"https://tce.by{event['image']}"

        # Strategy 6: Extract description from meta tags or content
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            event['description'] = meta_desc['content']
        else:
            # Try to find description in page content
            desc_selectors = [
                ('div', {'class': 'description'}),
                ('div', {'class': 'event-description'}),
                ('p', {'class': 'description'}),
            ]

            for selector, attrs in desc_selectors:
                element = soup.find(selector, attrs)
                if element:
                    event['description'] = element.text.strip()
                    break

        # If we found at least a title, consider this a valid event
        if event['title'] != 'Unknown':
            return event
        else:
            logging.info(f"Could not extract meaningful data from event ID {event_id}")
            return None

    except Exception as e:
        logging.error(f"Error parsing TCE event {event_id}: {e}")
        return None


def load_last_checked_id():
    """Load the last checked TCE event ID"""
    if os.path.exists(config.TCE_LAST_ID_FILE):
        try:
            with open(config.TCE_LAST_ID_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                last_id = data.get('last_checked_id', config.TCE_START_ID)
                logging.info(f"Loaded last checked TCE ID: {last_id}")
                return last_id
        except Exception as e:
            logging.error(f"Error loading last checked ID: {e}")
            return config.TCE_START_ID
    logging.info(f"No last checked ID file, using default: {config.TCE_START_ID}")
    return config.TCE_START_ID


def save_last_checked_id(last_id):
    """Save the last checked TCE event ID"""
    try:
        os.makedirs(os.path.dirname(config.TCE_LAST_ID_FILE), exist_ok=True)
        with open(config.TCE_LAST_ID_FILE, 'w', encoding='utf-8') as f:
            json.dump({'last_checked_id': last_id}, f, indent=2)
        logging.info(f"Saved last checked TCE ID: {last_id}")
    except Exception as e:
        logging.error(f"Error saving last checked ID: {e}")


def notify_tce_event_immediately(event, use_test_channel=False):
    """Send immediate notification about a single TCE event"""
    try:
        from telegram_notifier import send_channel_post

        # Format message for single event
        prefix = "🧪 [TEST] " if use_test_channel else ""
        message = f"{prefix}🎭 <b>НОВОЕ МЕРОПРИЯТИЕ TCE.BY!</b> 🎭\n\n"
        message += f"<b>{event['title']}</b>\n\n"

        # Date and time on same line if both available
        date_time_line = ""
        if event.get('date') and event['date'] != 'Unknown':
            date_time_line = f"📅 {event['date']}"

            if event.get('time') and event['time'] != 'Unknown':
                date_time_line += f" в {event['time']}"

            message += date_time_line + "\n"
        elif event.get('time') and event['time'] != 'Unknown':
            # Only time available
            message += f"🕒 {event['time']}\n"

        if event.get('venue') and event['venue'] != 'Unknown':
            message += f"📍 {event['venue']}\n"

        message += f"\n🎟 <a href='{event['url']}'>Подробнее и билеты</a>\n"

        if event.get('description') and len(event['description']) > 10:
            # Limit description to 300 characters
            desc = event['description'][:300]
            if len(event['description']) > 300:
                desc += "..."
            message += f"\n{desc}\n"

        message += "\n➖➖➖➖➖➖➖➖➖➖➖➖\n"

        # Use appropriate channel username
        channel_username = config.TEST_TELEGRAM_CHANNEL_USERNAME if use_test_channel else config.TELEGRAM_CHANNEL_USERNAME
        message += f"Подпишись {channel_username} для получения уведомлений!"

        # Send notification
        success = send_channel_post(message, disable_notification=False, use_test_channel=use_test_channel)

        if success:
            logging.info(f"✅ Immediate notification sent for TCE event ID {event['id']}: {event['title']}")
            if event['date'] != 'Unknown':
                logging.info(f"   📅 Date: {event['date']}" + (f" at {event['time']}" if event['time'] != 'Unknown' else ""))
        else:
            logging.error(f"❌ Failed to send immediate notification for TCE event ID {event['id']}")

        return success

    except Exception as e:
        logging.error(f"Error sending immediate TCE notification: {e}")
        return False


def check_tce_id_range(start_id=None, id_range=None, use_test_channel=False):
    """
    Check TCE event IDs with smart incremental logic.

    Logic:
    1. Start from base_id (last found event or config default)
    2. Check next id_range IDs (base_id+1 to base_id+id_range)
    3. If event found at ID X:
       - Send notification immediately
       - Save event
       - Set base_id = X (new starting point)
       - Check next id_range IDs from X (X+1 to X+id_range)
    4. If no events found in id_range IDs:
       - Stop checking
       - Save base_id for next run
    5. Repeat until no events found in id_range window

    This ensures:
    - We always check 10 IDs ahead of last found event
    - When event found, we check 10 more from that point
    - No IDs are skipped
    - Efficient scanning that adapts to event distribution
    """
    if start_id is None:
        start_id = load_last_checked_id()
    if id_range is None:
        id_range = config.TCE_ID_RANGE

    logging.info(f"=" * 60)
    logging.info(f"Starting TCE ID check from base {start_id}")
    logging.info(f"Will check {id_range} IDs ahead after each found event")
    logging.info(f"=" * 60)

    found_events = []
    base_id = start_id
    total_checked = 0

    while True:
        # Check next id_range IDs from base_id
        check_start = base_id + 1
        check_end = base_id + id_range + 1

        logging.info(f"\n🔍 Checking IDs {check_start} to {check_end - 1} (base: {base_id})")

        found_in_this_range = False
        highest_found_id = base_id

        for current_id in range(check_start, check_end):
            try:
                # Construct URL
                url = f"{config.TCE_BASE_URL}?base={config.TCE_BASE_PARAM}&data={current_id}"

                logging.info(f"  Checking ID {current_id}...")
                total_checked += 1

                # Fetch page
                html = fetch_tce_page(url)

                # Parse event
                event = parse_tce_event(html, current_id, url)

                if event:
                    logging.info(f"  ✅ Found valid event at ID {current_id}: {event['title']}")

                    # Add to found events
                    found_events.append(event)

                    # Send immediate notification
                    notify_tce_event_immediately(event, use_test_channel=use_test_channel)

                    # Save event to database
                    save_single_tce_event(event)

                    # Mark that we found something in this range
                    found_in_this_range = True

                    # Update highest found ID
                    if current_id > highest_found_id:
                        highest_found_id = current_id

                    logging.info(f"  📌 Will check {id_range} more IDs after finishing this range")
                else:
                    logging.info(f"  ❌ No event at ID {current_id}")

                # Be respectful to the server
                time.sleep(2)

            except Exception as e:
                logging.error(f"  ⚠️  Error checking TCE ID {current_id}: {e}")
                continue

        # After checking this range
        if found_in_this_range:
            # We found event(s), update base to highest found and continue
            base_id = highest_found_id
            logging.info(f"\n✅ Found event(s) in range! New base: {base_id}")
            logging.info(f"📌 Will now check next {id_range} IDs from {base_id}")

            # Save progress
            save_last_checked_id(base_id)
        else:
            # No events found in this range, stop
            logging.info(f"\n❌ No events found in IDs {check_start}-{check_end - 1}")
            logging.info(f"🛑 Stopping search")

            # Save the base_id as starting point for next run
            save_last_checked_id(base_id)
            break

    logging.info(f"\n" + "=" * 60)
    logging.info(f"Search complete!")
    logging.info(f"Total IDs checked: {total_checked}")
    logging.info(f"Events found: {len(found_events)}")
    logging.info(f"Last event found at ID: {base_id}")
    logging.info(f"Next run will start from ID {base_id} (checking {base_id + 1} onwards)")
    logging.info(f"=" * 60)

    return found_events


def save_single_tce_event(event):
    """Save a single TCE event to the database"""
    try:
        # Load existing events
        existing_events = load_previous_tce_data()

        # Check if event already exists
        event_exists = any(e['id'] == event['id'] for e in existing_events)

        if not event_exists:
            existing_events.append(event)
            save_tce_data(existing_events)
            logging.info(f"Saved new TCE event ID {event['id']} to database")
        else:
            logging.info(f"TCE event ID {event['id']} already in database")

    except Exception as e:
        logging.error(f"Error saving single TCE event: {e}")


def load_previous_tce_data():
    """Load previously saved TCE event data"""
    if os.path.exists(config.TCE_DATA_FILE):
        try:
            with open(config.TCE_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logging.info(f"Successfully loaded {len(data)} TCE events from {config.TCE_DATA_FILE}")
                return data
        except Exception as e:
            logging.error(f"Error loading previous TCE data: {e}")
            return []
    logging.info(f"No previous TCE data file exists")
    return []


def save_tce_data(events):
    """Save TCE event data"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(config.TCE_DATA_FILE), exist_ok=True)

        with open(config.TCE_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        logging.info(f"Successfully saved {len(events)} TCE events to {config.TCE_DATA_FILE}")
    except Exception as e:
        logging.error(f"Error saving TCE data: {e}")


def compare_tce_data(old_data, new_data):
    """Compare old and new TCE data to find new events"""
    old_ids = {event['id'] for event in old_data}
    new_events = [event for event in new_data if event['id'] not in old_ids]

    logging.info(f"Found {len(new_events)} new TCE events")
    return new_events


def check_for_new_tce_events(use_test_channel=False):
    """
    Check for new TCE events with immediate notifications.

    The function will:
    1. Start from the last checked ID (or configured start ID)
    2. Check IDs incrementally
    3. When an event is found:
       - Send immediate notification
       - Save the event
       - Reset the 404 counter
       - Continue checking
    4. Stop after finding TCE_ID_RANGE consecutive 404s

    Args:
        use_test_channel: If True, send to test channel instead of production

    Returns:
        List of found events (for backward compatibility)
    """
    try:
        logging.info("=" * 60)
        logging.info("Starting TCE.BY monitoring with immediate notifications")
        logging.info("=" * 60)

        # Check ID range with immediate notifications
        current_events = check_tce_id_range(use_test_channel=use_test_channel)

        if current_events:
            logging.info(f"✅ Total: Found and notified {len(current_events)} new TCE events")
        else:
            logging.info("No new TCE events found in this check")

        return current_events

    except Exception as e:
        logging.error(f"Error checking for new TCE events: {e}")
        return []
