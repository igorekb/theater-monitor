"""Module for sending Telegram notifications about new performances"""
import logging
import requests
import config

def send_telegram_message(message, bot_token=None, chat_id=None):
    """
    Send a message via Telegram bot
    
    Args:
        message: The message text to send
        bot_token: The Telegram bot token (if None, uses config value)
        chat_id: The chat ID to send to (if None, uses config value)
    
    Returns:
        Success status (True/False)
    """
    bot_token = bot_token or config.TELEGRAM_BOT_TOKEN
    chat_id = chat_id or config.TELEGRAM_CHAT_ID
    
    if not bot_token or not chat_id:
        logging.error("Telegram bot token or chat ID not provided")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        response = requests.post(
            url, 
            json={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            },
            timeout=10
        )
        
        response.raise_for_status()
        logging.info(f"Telegram message sent successfully")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False

def format_performance_notification(performances):
    """
    Format a list of performances into a readable Telegram message
    
    Args:
        performances: List of performance dictionaries
        
    Returns:
        Formatted message string
    """
    if not performances:
        return "No new performances found."
        
    message = f"🎭 <b>{len(performances)} Новые спектакли{'s' if len(performances) > 1 else ''} найдены!</b>\n\n"
    
    for i, perf in enumerate(performances, 1):
        message += f"<b>{i}. {perf['title']}</b>\n"
        message += f"📅 {perf['day']}\n"
        message += f"🕒 {perf['time']}\n"
        message += f"🎟 <a href='{perf['ticket_link']}'>Купить Билеты</a>\n\n"
    
    message += "Visit <a href='https://puppet-minsk.by/afisha'>puppet-minsk.by/afisha</a> всё расписание."
    
    return message

def notify_about_performances(performances):
    """
    Send Telegram notification about new performances
    
    Args:
        performances: List of performance dictionaries
        
    Returns:
        Success status (True/False)
    """
    if not performances:
        logging.info("No performances to notify about")
        return True
        
    message = format_performance_notification(performances)
    return send_channel_post(message, disable_notification=False)


def format_performance_notification(performances):
    """
    Format a list of performances into a readable Telegram message for a channel
    
    Args:
        performances: List of performance dictionaries
        
    Returns:
        Formatted message string
    """
    if not performances:
        return "No new performances found."
        
    message = f"🎭 <b>НОВЫЕ СПЕКТАКЛИ В ПРОДАЖЕ!</b> 🎭\n\n"
    
    for i, perf in enumerate(performances, 1):
        message += f"<b>{perf['title']}</b>\n"
        message += f"📅 {perf['day']}\n"
        message += f"🕒 {perf['time']}\n"
        message += f"🎟 <a href='{perf['ticket_link']}'>Купить Билеты</a>\n\n"
    
    message += "➖➖➖➖➖➖➖➖➖➖➖➖\n"
    message += f"Подпишись {config.TELEGRAM_CHANNEL_USERNAME} для получения уведомлений!\n"
    message += "Все выступления на сайте: <a href='https://puppet-minsk.by/afisha'>puppet-minsk.by/afisha</a>"
    
    return message


def send_channel_post(message, disable_notification=True):
    """
    Send a channel post via Telegram bot
    
    Args:
        message: The message text to send
        disable_notification: Whether to send silently (no notification sound)
    
    Returns:
        Success status (True/False)
    """
    bot_token = config.TELEGRAM_BOT_TOKEN
    channel_id = config.TELEGRAM_CHAT_ID
    
    if not bot_token or not channel_id:
        logging.error("Telegram bot token or channel ID not provided")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        response = requests.post(
            url, 
            json={
                'chat_id': channel_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False,
                'disable_notification': disable_notification
            },
            timeout=10
        )
        
        response.raise_for_status()
        logging.info(f"Channel post sent successfully to {channel_id}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send channel post: {e}")
        return False