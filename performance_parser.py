"""Module for parsing theater performance data"""
import logging
import requests
from bs4 import BeautifulSoup
import time

def fetch_page(url, max_retries=3, retry_delay=5):
    """Fetch the theater page with error handling and retries"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for attempt in range(max_retries):
        try:
            logging.info(f"Fetching content from {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # Raise exception for HTTP errors
            response.encoding = 'utf-8'  # Ensure proper encoding for Cyrillic characters
            logging.info(f"Successfully fetched page, status code: {response.status_code}")
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching page (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error("Max retries reached. Failed to fetch page.")
                raise

def parse_performances(html, base_url="https://puppet-minsk.by"):
    """Extract performance information from the HTML with multiple fallback strategies"""
    soup = BeautifulSoup(html, 'html.parser')
    performances = []

    # Strategy 1: Try current selectors (afisha_item)
    performance_items = soup.find_all('div', class_='afisha_item')

    # Strategy 2: Fallback to alternative class names if nothing found
    if not performance_items:
        logging.warning("No 'afisha_item' found, trying alternative selectors")
        performance_items = soup.find_all('div', class_='performance')

    if not performance_items:
        performance_items = soup.find_all('div', class_='event')

    if not performance_items:
        performance_items = soup.find_all('div', class_='show')

    if not performance_items:
        performance_items = soup.find_all('article', class_=['event', 'performance', 'show'])

    # Strategy 3: Try to find by structure (divs with specific children)
    if not performance_items:
        logging.warning("Standard selectors failed, trying structural analysis")
        # Look for divs that contain date/time patterns
        all_divs = soup.find_all('div')
        for div in all_divs:
            # Check if div contains date-like and title-like elements
            has_date = bool(div.find(string=lambda text: text and any(month in text.lower() for month in
                ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'])))
            has_time = bool(div.find(string=lambda text: text and ':' in text and len(text.strip()) < 10))

            if has_date or has_time:
                performance_items.append(div)

    logging.info(f"Found {len(performance_items)} performance items in HTML")

    for item in performance_items:
        try:
            # Extract date and day with multiple fallbacks
            day = extract_with_fallbacks(item,
                ['.afisha-day', '.day', '.date', '.event-date', 'time'],
                attribute=None)

            # Extract time with multiple fallbacks
            time_value = extract_with_fallbacks(item,
                ['.afisha-time', '.time', '.event-time', '.show-time'],
                attribute=None)

            # Extract title with multiple fallbacks
            title = extract_with_fallbacks(item,
                ['.afisha-title', '.title', '.event-title', '.show-title', 'h2', 'h3', 'h4'],
                attribute=None)

            # If still no title, try to find the longest text in the item
            if title == "Unknown":
                texts = [t.strip() for t in item.stripped_strings if len(t.strip()) > 5]
                if texts:
                    title = max(texts, key=len)

            # Extract image URL with multiple fallbacks
            image = ""
            img_elem = item.find('img')
            if img_elem:
                image = img_elem.get('src', '') or img_elem.get('data-src', '') or img_elem.get('data-lazy', '')

            if image and not image.startswith(('http://', 'https://')):
                # Make relative URLs absolute
                image = f"{base_url}{image}" if not image.startswith('/') else f"{base_url}{image}"

            image_alt = img_elem.get('alt', '') if img_elem else ""

            # Extract ticket link with multiple fallbacks
            ticket_link = ""
            link_elem = item.find('a', href=True)
            if link_elem:
                ticket_link = link_elem['href']

            if ticket_link and not ticket_link.startswith(('http://', 'https://')):
                # Make relative URLs absolute
                ticket_link = f"{base_url}{ticket_link}" if not ticket_link.startswith('/') else f"{base_url}{ticket_link}"

            # Extract month classification
            month_classes = [cls for cls in item.get('class', []) if 'item_mounth-' in cls or 'month-' in cls]
            month_class = month_classes[0] if month_classes else "Unknown"

            # Only add performance if we have at least a title
            if title and title != "Unknown":
                # Create performance object
                performance = {
                    'day': day,
                    'time': time_value,
                    'title': title,
                    'image': image,
                    'image_alt': image_alt,
                    'ticket_link': ticket_link,
                    'month_class': month_class
                }

                performances.append(performance)

        except Exception as e:
            logging.error(f"Error parsing performance: {e}")

    return performances


def extract_with_fallbacks(item, selectors, attribute=None):
    """Try multiple CSS selectors with fallbacks"""
    for selector in selectors:
        try:
            if selector.startswith('.') or selector.startswith('#'):
                elem = item.select_one(selector)
            else:
                elem = item.find(selector)

            if elem:
                if attribute:
                    value = elem.get(attribute)
                    if value:
                        return value
                else:
                    text = elem.text.strip()
                    if text:
                        return text
        except Exception as e:
            logging.debug(f"Selector {selector} failed: {e}")
            continue

    return "Unknown"