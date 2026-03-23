"""Module for monitoring TCE.BY events via search API with Anubis bypass"""
import json
import os
import logging
import random
import time
import calendar
from datetime import datetime, date as _date
import requests
import config

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    sync_playwright = None
    PlaywrightTimeout = Exception
    logging.warning("Playwright not found. Install with: pip install playwright && playwright install chromium")


def load_processed_ids() -> set:
    """Load set of already-processed event IDs from tce_processed_ids.json"""
    if os.path.exists(config.TCE_PROCESSED_IDS_FILE):
        try:
            with open(config.TCE_PROCESSED_IDS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                ids = set(data.get('processed_ids', []))
                logging.info(f"Loaded {len(ids)} processed event IDs")
                return ids
        except Exception as e:
            logging.error(f"Error loading processed IDs: {e}")
    return set()


def save_processed_ids(ids: set) -> None:
    """Save set of processed event IDs to tce_processed_ids.json"""
    try:
        os.makedirs(os.path.dirname(config.TCE_PROCESSED_IDS_FILE), exist_ok=True)
        with open(config.TCE_PROCESSED_IDS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'processed_ids': sorted(ids)}, f, indent=2)
        logging.info(f"Saved {len(ids)} processed event IDs")
    except Exception as e:
        logging.error(f"Error saving processed IDs: {e}")


def _extract_event_list(data) -> list:
    """Extract the events list from an API response that may be a list or a dict wrapper."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        known_keys = ('data', 'items', 'shows', 'events', 'results', 'list')
        for key in known_keys:
            if key in data:
                val = data[key]
                return val if isinstance(val, list) else []  # null/false/0 → empty month
        for val in data.values():
            if isinstance(val, list):
                return val
        logging.warning("Unexpected API response shape. Keys: %s", list(data.keys()))
    return []


def _fetch_search_api_with_playwright() -> list:
    """Navigate to tce.by via Playwright (Anubis bypass), call search API from browser context"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=config.USE_HEADLESS,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--no-first-run',
                    '--no-default-browser-check',
                ]
            )
            context = browser.new_context(
                user_agent=config.USER_AGENT,
                viewport={'width': 1920, 'height': 1080},
                locale='ru-RU',
                color_scheme='light',
                has_touch=False,
                is_mobile=False,
                extra_http_headers={
                    "Accept-Language": config.ACCEPT_LANGUAGE,
                    "DNT": "1",
                    "Upgrade-Insecure-Requests": "1",
                }
            )
            page = context.new_page()

            # Patch automation detection before any page script runs
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU', 'ru', 'en-US', 'en']});
                window.chrome = {runtime: {}};
            """)

            # Land on homepage first — natural entry point, establishes session
            logging.info("Navigating to tce.by homepage...")
            page.goto("https://tce.by/", wait_until='networkidle',
                      timeout=config.BROWSER_TIMEOUT * 1000)
            time.sleep(random.uniform(2, 4))

            # Navigate to search page — triggers Anubis clearance
            logging.info("Navigating to tce.by/search.html...")
            page.goto("https://tce.by/search.html", wait_until='networkidle',
                      timeout=config.BROWSER_TIMEOUT * 1000)
            time.sleep(random.uniform(4, 8))  # Anubis JS challenge + page settling

            # Simulate natural user interaction
            page.evaluate(f"window.scrollBy(0, {random.randint(150, 400)})")
            time.sleep(random.uniform(0.5, 1.5))
            page.mouse.move(random.randint(200, 1200), random.randint(150, 700))

            # Build month windows: current month + TCE_MONTHS_AHEAD future months
            today = _date.today()
            months = []
            for offset in range(config.TCE_MONTHS_AHEAD + 1):
                year = today.year + (today.month - 1 + offset) // 12
                month = (today.month - 1 + offset) % 12 + 1
                last_day = calendar.monthrange(year, month)[1]
                # For the current month start from today to skip already-past events
                date_begin = today.strftime('%Y-%m-%d') if offset == 0 else f"{year}-{month:02d}-01"
                months.append({
                    'date_begin': date_begin,
                    'date_end':   f"{year}-{month:02d}-{last_day:02d}",
                })

            # One POST per month — reuses the same Anubis-cleared session
            _JS_FETCH = """
                async (args) => {
                    try {
                        const body = new URLSearchParams({
                            bk_id: '', date_begin: args.date_begin, date_end: args.date_end,
                            tags: '', server_key: args.server_key,
                            loc_id: '0', hall_id: '0', order_id: '0', type: ''
                        }).toString();
                        const r = await fetch('/index.php?view=shows&action=find&kind=text', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'Accept': 'application/json, text/javascript, */*; q=0.01',
                                'X-Requested-With': 'XMLHttpRequest'
                            },
                            body: body
                        });
                        if (!r.ok) return {_error: r.status};
                        return await r.json();
                    } catch(e) { return {_error: e.toString()}; }
                }
            """

            all_events = []
            seen_ids = set()
            for m in months:
                logging.info(f"Fetching puppet events {m['date_begin']} → {m['date_end']}")
                chunk = page.evaluate(_JS_FETCH, {**m, 'server_key': config.TCE_BASE_PARAM})
                if isinstance(chunk, dict) and '_error' in chunk:
                    logging.error(f"API error for {m['date_begin']}: {chunk}")
                    continue
                events = _extract_event_list(chunk)
                logging.info(f"  {m['date_begin'][:7]}: {len(events)} events")
                for e in events:
                    if e.get('bk_id') not in seen_ids:
                        seen_ids.add(e['bk_id'])
                        all_events.append(e)
                if len(events) == 0:
                    logging.info("  No events this month — stopping early")
                    break
                time.sleep(random.uniform(1.5, 4.0))  # think-time between API calls

            browser.close()

            logging.info(f"Total unique puppet events across all months: {len(all_events)}")
            return all_events

    except PlaywrightTimeout as e:
        logging.error(f"Playwright timeout fetching search API: {e}")
        raise
    except Exception as e:
        logging.error(f"Error fetching search API with Playwright: {e}")
        raise


def fetch_puppet_events_from_api() -> list:
    """
    Fetch puppet theatre events from the tce.by search API.
    Filters by server_key == TCE_BASE_PARAM.
    Returns list of raw API event dicts (each has bk_id, show_name, bk_date, etc.).
    """
    raw = _fetch_search_api_with_playwright()

    logging.info(f"Search API: {len(raw)} puppet theatre events (server-filtered by server_key)")
    return raw


def _build_event_from_api(api_event: dict) -> dict:
    """Build a normalised event dict from a search API response item."""
    event_id = api_event['bk_id']
    url = f"{config.TCE_BASE_URL}?base={config.TCE_BASE_PARAM}&data={event_id}"

    date_str, time_str = 'Unknown', 'Unknown'
    bk_date = api_event.get('bk_date', '')
    try:
        from datetime import datetime as _dt
        d = _dt.strptime(bk_date, '%Y-%m-%d %H:%M:%S')
        date_str = d.strftime('%d.%m.%Y')
        time_str = d.strftime('%H:%M')
    except (ValueError, TypeError):
        pass

    venue = api_event.get('hall_name', 'Unknown')
    address = api_event.get('hall_address', '')
    if address:
        venue = f"{venue}, {address}"

    return {
        'id': event_id,
        'url': url,
        'title': api_event.get('show_name', 'Unknown'),
        'date': date_str,
        'time': time_str,
        'venue': venue,
        'description': api_event.get('owner_name', ''),
        'image': '',
        'found_at': datetime.now().isoformat(),
    }


def send_channel_post(message, disable_notification=True, use_test_channel=False):
    """Send a message to the configured Telegram channel."""
    bot_token = config.TELEGRAM_BOT_TOKEN
    channel_id = config.TEST_TELEGRAM_CHAT_ID if use_test_channel else config.TELEGRAM_CHAT_ID
    channel_type = "test" if use_test_channel else "production"

    if not bot_token or not channel_id:
        logging.error(f"Telegram bot token or {channel_type} channel ID not configured")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        response = requests.post(url, json={
            'chat_id': channel_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False,
            'disable_notification': disable_notification,
        }, timeout=10)

        if not response.ok:
            error = response.json()
            logging.error(f"Telegram API error: {error.get('description', response.text)}")
        response.raise_for_status()
        logging.info(f"Notification sent to {channel_type} channel ({channel_id})")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send to {channel_type} channel: {e}")
        return False


def _format_event_line(event) -> str:
    """Format a single event as a compact line: title, date/time, link."""
    line = f"<b>{event['title']}</b>"
    if event.get('date') and event['date'] != 'Unknown':
        dt = f"📅 {event['date']}"
        if event.get('time') and event['time'] != 'Unknown':
            dt += f" в {event['time']}"
        line += f"\n{dt}"
    elif event.get('time') and event['time'] != 'Unknown':
        line += f"\n🕒 {event['time']}"
    line += f"\n🎟 <a href='{event['url']}'>Билеты</a>"
    return line


def notify_tce_events(events, use_test_channel=False):
    """Send new TCE events to Telegram, batching 10 events per message."""
    BATCH_SIZE = 10
    prefix = "🧪 [TEST] " if use_test_channel else ""
    channel_username = config.TEST_TELEGRAM_CHANNEL_USERNAME if use_test_channel else config.TELEGRAM_CHANNEL_USERNAME
    total = len(events)
    batches = [events[i:i + BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]
    all_ok = True

    for batch_num, batch in enumerate(batches, 1):
        try:
            count = len(batch)
            if total <= BATCH_SIZE:
                header = f"{prefix}🎭 <b>НОВЫЙ СПЕКТАКЛЬ!</b>" if count == 1 else f"{prefix}🎭 <b>НОВЫЕ СПЕКТАКЛИ! ({count})</b>"
            else:
                header = f"{prefix}🎭 <b>НОВЫЕ СПЕКТАКЛИ! ({batch_num}/{len(batches)})</b>"

            blocks = "\n\n".join(_format_event_line(e) for e in batch)
            message = f"{header}\n\n{blocks}\n\n➖➖➖➖➖➖➖➖➖➖➖➖\nПодпишись {channel_username} для получения уведомлений!"

            success = send_channel_post(message, disable_notification=False, use_test_channel=use_test_channel)
            if success:
                logging.info(f"✅ Notification sent (batch {batch_num}/{len(batches)}): {', '.join(e['title'] for e in batch)}")
            else:
                logging.error(f"❌ Failed to send notification batch {batch_num}/{len(batches)}")
                all_ok = False
            if batch_num < len(batches):
                time.sleep(2)
        except Exception as e:
            logging.error(f"Error sending TCE notification batch {batch_num}: {e}")
            all_ok = False

    return all_ok


def check_for_new_tce_events(use_test_channel=False, notify=True) -> list:
    """
    Main entry point. Fetches puppet theatre events from the tce.by search API,
    processes only IDs not yet seen, sends immediate notifications, and persists
    the updated processed-ID set.

    Returns list of newly found event dicts.
    """
    logging.info("=" * 60)
    logging.info("Starting TCE.BY puppet theatre monitoring (search-API mode)")
    logging.info("=" * 60)

    # Step 1: get puppet theatre events from search API (single browser session)
    api_events = fetch_puppet_events_from_api()
    if not api_events:
        logging.info("No puppet theatre events returned by search API")
        return []

    fetched_ids = {e['bk_id'] for e in api_events}

    # Step 2: find which are new
    processed_ids = load_processed_ids()
    new_api_events = [e for e in api_events if e['bk_id'] not in processed_ids]
    logging.info(f"API events: {len(api_events)}, already processed: {len(processed_ids)}, new: {len(new_api_events)}")

    if not new_api_events:
        logging.info("No new puppet theatre events")
        save_processed_ids(processed_ids | fetched_ids)
        return []

    # Step 3: build events
    new_events = []
    for api_event in new_api_events:
        try:
            event = _build_event_from_api(api_event)
            logging.info(f"  New event: {event['title']} on {event['date']} at {event['time']}")
            save_single_tce_event(event)
            new_events.append(event)
            processed_ids.add(api_event['bk_id'])
        except Exception as e:
            logging.error(f"Error processing event bk_id={api_event.get('bk_id')}: {e}")
            processed_ids.add(api_event.get('bk_id'))

    # Step 4: send one combined notification for all new events
    if notify and new_events:
        notify_tce_events(new_events, use_test_channel=use_test_channel)
    elif new_events:
        logging.info(f"  Skipping notification (--no-notify mode)")

    # Step 5: persist updated processed IDs (all fetched, including already-seen)
    save_processed_ids(processed_ids | fetched_ids)

    logging.info(f"Done. Found and notified {len(new_events)} new puppet theatre events")
    return new_events


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


