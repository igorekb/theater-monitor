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
    """Extract performance information from the HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    performances = []
    
    # Find all performance items
    performance_items = soup.find_all('div', class_='afisha_item')
    logging.info(f"Found {len(performance_items)} performance items in HTML")
    
    for item in performance_items:
        try:
            # Extract date and day
            day_elem = item.select_one('.afisha-day')
            day = day_elem.text.strip() if day_elem else "Unknown"
            
            # Extract time
            time_elem = item.select_one('.afisha-time')
            time = time_elem.text.strip() if time_elem else "Unknown"
            
            # Extract title
            title_elem = item.select_one('.afisha-title')
            title = title_elem.text.strip() if title_elem else "Unknown"
            
            # Extract image URL
            img_elem = item.select_one('img')
            image = img_elem['src'] if img_elem and 'src' in img_elem.attrs else ""
            if image and not image.startswith(('http://', 'https://')):
                # Make relative URLs absolute
                image = f"{base_url}{image}" if not image.startswith('/') else f"{base_url}{image}"
            image_alt = img_elem['alt'] if img_elem and 'alt' in img_elem.attrs else ""
            
            # Extract ticket link
            ticket_link_elem = item.select_one('a')
            ticket_link = ticket_link_elem['href'] if ticket_link_elem and 'href' in ticket_link_elem.attrs else ""
            if ticket_link and not ticket_link.startswith(('http://', 'https://')):
                # Make relative URLs absolute
                ticket_link = f"{base_url}{ticket_link}" if not ticket_link.startswith('/') else f"{base_url}{ticket_link}"
            
            # Extract month classification
            month_classes = [cls for cls in item.get('class', []) if 'item_mounth-' in cls]
            month_class = month_classes[0] if month_classes else "Unknown"
            
            # Create performance object
            performance = {
                'day': day,
                'time': time,
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