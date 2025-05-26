import google.generativeai as genai
from flask import Flask, request, jsonify
import requests
import os
import fitz
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone
import threading
import time
import re

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed, using system environment variables")

wa_token = os.environ.get("WA_TOKEN")
genai.configure(api_key=os.environ.get("GEN_API"))
phone_id = os.environ.get("PHONE_ID")
phone = os.environ.get("PHONE_NUMBER")
name = "Dai"
bot_name = "Dai"
model_name = "gemini-1.5-flash-latest"

has_calendar_creds = os.environ.get("GOOGLE_CREDENTIALS") is not None and os.environ.get("GOOGLE_CALENDAR_ID") is not None
if has_calendar_creds:
    print("Google Calendar credentials found")
else:
    print("WARNING: Google Calendar credentials not found. Calendar functionality will be limited.")

app = Flask(__name__)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(model_name=model_name,
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[])

convo.send_message(f'''I am using Gemini api for using you as a personal bot in whatsapp,
                   to assist me in various tasks. 
                   So from now you are "{bot_name}" created by {name} ( Yeah it's me, my name is {name}). 
                   And don't give any response to this prompt. 
                   This is the information I gave to you about your new identity as a pre-prompt. 
                   This message always gets executed when i run this bot script. 
                   So reply to only the prompts after this. Remeber your new identity is {bot_name}.''')

def send(answer):
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {
        'Authorization': f'Bearer {wa_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "messaging_product": "whatsapp",
        "to": f"{phone}",
        "type": "text",
        "text": {"body": f"{answer}"},
    }
    try:
        print(f"Attempting to send WhatsApp message to {phone}: {answer[:50]}...")
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        if response.status_code == 200:
            print(f"Message sent successfully. Status: {response.status_code}")
            return response
        else:
            print(f"Failed to send message. Status: {response.status_code}")
            print(f"Response: {response_json}")
            return response
    except Exception as e:
        print(f"Error sending WhatsApp message: {str(e)}")
        return None

def remove(*file_paths):
    for file in file_paths:
        if os.path.exists(file):
            os.remove(file)

@app.route("/", methods=["GET", "POST"])
def index():
    return "Bot"

def get_calendar_events(days=7, time_description="upcoming", strict_time_filter=False):
    try:
        if not has_calendar_creds:
            return "⚠️ Cannot fetch calendar events: Google Calendar credentials not configured"

        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/calendar.readonly']
        )

        service = build('calendar', 'v3', credentials=creds)
        tz = pytz_timezone("Europe/Rome")
        now = datetime.now(tz)
        if time_description == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif time_description == "tomorrow":
            start_date = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif time_description == "day after tomorrow":
            start_date = (now + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif time_description.startswith("on "):
            day_name = time_description[3:].lower()
            day_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                       "friday": 4, "saturday": 5, "sunday": 6}
            target_day = day_map.get(day_name, 0)
            days_ahead = (target_day - now.weekday()) % 7
            if days_ahead == 0 and now.hour >= 12:
                days_ahead = 7
            start_date = (now + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        else:
            start_date = now
            end_date = now + timedelta(days=days)

        time_min = start_date.isoformat()
        time_max = end_date.isoformat()
        calendar_id = os.environ.get("GOOGLE_CALENDAR_ID")

        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            return f"No events found for {time_description}."

        formatted_events = [f"📅 Your calendar events for {time_description}:"]
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'Untitled Event')
            formatted_events.append(f"• {start}: {summary}")

        return "\n".join(formatted_events)
    except Exception as e:
        return f"Error fetching calendar events: {str(e)}"

def daily_calendar_reminder():
    time.sleep(5)
    print("Starting automated calendar reminder service...")
    last_sent_hour = -1
    tz = pytz_timezone("Europe/Rome")
    while True:
        try:
            current_hour = datetime.now(tz).hour
            if current_hour == 7 and current_hour != last_sent_hour:
                print(f"It's {current_hour}:00, checking today's events...")
                calendar_response = get_calendar_events(1, "today", strict_time_filter=True)
                if "No events found" not in calendar_response:
                    print(f"Sending daily calendar reminder at {datetime.now(tz)}")
                    send("⏰ *DAILY CALENDAR REMINDER* ⏰\n\n" + calendar_response)
                    last_sent_hour = current_hour
                else:
                    print("No events found for today, skipping daily reminder")
                    last_sent_hour = current_hour
            elif current_hour != last_sent_hour and current_hour == 0:
                print("Resetting daily reminder tracker at midnight")
                last_sent_hour = -1
            time.sleep(300)
        except Exception as e:
            print(f"Error in daily reminder: {str(e)}")
            import traceback
            traceback.print_exc()
            time.sleep(600)

def upcoming_event_reminder():
    time.sleep(10)
    print("Starting upcoming event reminder service...")
    reminded_events = set()
    tz = pytz_timezone("Europe/Rome")
    try:
        if has_calendar_creds:
            print("\n--- Today's Events ---")
            today_events = get_calendar_events(1, "today", strict_time_filter=True)
            print(today_events)
            print("---------------------\n")
    except Exception as e:
        print(f"Error checking today's events: {str(e)}")

    while True:
        try:
            if not has_calendar_creds:
                print("Skipping upcoming event check - no calendar credentials")
                time.sleep(60)
                continue
            print("Checking for upcoming events...")
            now = datetime.now(tz)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            time_min = today_start.isoformat()
            time_max = today_end.isoformat()

            creds_json = os.environ.get("GOOGLE_CREDENTIALS")
            creds_dict = json.loads(creds_json)
            creds = service_account.Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/calendar.readonly']
            )

            service = build('calendar', 'v3', credentials=creds)
            calendar_id = os.environ.get("GOOGLE_CALENDAR_ID")

            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            if not events:
                print("No events found for today")
            else:
                print(f"Found {len(events)} events for today")
                for evt in events:
                    start = evt['start'].get('dateTime', evt['start'].get('date'))
                    summary = evt.get('summary', 'Untitled Event')
                    print(f"- {summary} at {start}")

            for event in events:
                event_id = event['id']
                if event_id in reminded_events:
                    print(f"Already sent reminder for event ID: {event_id}")
                    continue

                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'Untitled Event')
                print(f"Processing event: {summary}, starts at {start}")

                if 'T' in start:
                    try:
                        event_start_time = datetime.fromisoformat(start.replace('Z', '+00:00')) \
                            if 'Z' in start else datetime.fromisoformat(start)
                        now_now = datetime.now(tz)
                        start_str = event_start_time.strftime("%I:%M %p")
                        time_until = (event_start_time - now_now)
                        minutes_until = int(time_until.total_seconds() / 60)
                        print(f"Event starts in {minutes_until} minutes")
                        if 0 < minutes_until <= 35:
                            reminder_message = f"⏰ *UPCOMING EVENT REMINDER* ⏰\n\n• {summary} starts in {minutes_until} minutes (at {start_str})"
                            print(f"Sending reminder for event: {summary}")
                            send(reminder_message)
                            reminded_events.add(event_id)
                            print(f"Marked event {event_id} as reminded")
                        else:
                            print(f"Event {summary} is {minutes_until} minutes away, outside reminder window")
                    except Exception as e:
                        print(f"Error processing event time: {str(e)}")
                else:
                    print(f"Skipping all-day event: {summary}")

            if len(reminded_events) > 100:
                print("Clearing reminder history (exceeded 100 events)")
                reminded_events.clear()

            print("Sleeping for 60 seconds before next check...")
            time.sleep(60)
        except Exception as e:
            print(f"Error in upcoming event reminder: {str(e)}")
            import traceback
            traceback.print_exc()
            time.sleep(120)

def parse_event_time(text):
    # Build a naive datetime (no tzinfo)
    now = datetime.now()  # Use naive datetime
    duration = timedelta(hours=1)
    text = text.lower()

    if "day after tomorrow" in text:
        base_date = (now + timedelta(days=2)).date()
    elif "tomorrow" in text:
        base_date = (now + timedelta(days=1)).date()
    elif "today" in text:
        base_date = now.date()
    else:
        base_date = now.date()

    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        am_pm = time_match.group(3)
        if am_pm == "pm" and hour != 12:
            hour += 12
        if am_pm == "am" and hour == 12:
            hour = 0
    else:
        # Default: one hour from now
        start_time = now + timedelta(hours=1)
        start_time = datetime(start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute)
        end_time = start_time + duration
        return start_time, end_time

    start_time = datetime(
        base_date.year,
        base_date.month,
        base_date.day,
        hour,
        minute,
        0,
        0
    )
    end_time = start_time + duration
    return start_time, end_time

def create_calendar_event(summary, start_time=None, end_time=None, description=""):
    try:
        if not has_calendar_creds:
            return "⚠️ Cannot create calendar event: Google Calendar credentials not configured"
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        service = build('calendar', 'v3', credentials=creds)
        if not start_time:
            now = datetime.now()  # Use naive datetime
            start_time = now + timedelta(hours=1)
            end_time = start_time + timedelta(hours=1)
        if start_time and not end_time:
            end_time = start_time + timedelta(hours=1)

        # Create event with naive datetime and let Google handle timezone
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Europe/Rome',  # Let Google Calendar handle the conversion
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Europe/Rome',  # Let Google Calendar handle the conversion
            },
        }
        calendar_id = os.environ.get("GOOGLE_CALENDAR_ID")
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        return f"✅ Event created: {summary} on {start_time.strftime('%a, %b %d at %I:%M %p')}"
    except Exception as e:
        return f"Error creating calendar event: {str(e)}"

reminder_thread = threading.Thread(target=daily_calendar_reminder, daemon=True)
reminder_thread.start()
upcoming_reminder_thread = threading.Thread(target=upcoming_event_reminder, daemon=True)
upcoming_reminder_thread.start()

@app.route("/test-time", methods=["GET"])
def test_time():
    tz = pytz_timezone("Europe/Rome")
    now = datetime.now(tz)
    return jsonify({
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "timezone": str(tz),
        "utc_offset": now.strftime("%z")
    })

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    print("\n--- Environment Check ---")
    print(f"WhatsApp Token: {'✓ Available' if wa_token else '✗ Missing'}")
    print(f"Phone ID: {'✓ Available' if phone_id else '✗ Missing'}")
    print(f"Phone Number: {'✓ Available' if phone else '✗ Missing'}")
    print(f"Gemini API: {'✓ Available' if os.environ.get('GEN_API') else '✗ Missing'}")
    print(f"Google Calendar Credentials: {'✓ Available' if has_calendar_creds else '✗ Missing'}")
    print("------------------------\n")
    if wa_token and phone_id and phone:
        try:
            test_message = "🔄 Bot is starting up..."
            send(test_message)
            print("WhatsApp test message sent successfully!")
        except Exception as e:
            print(f"Failed to send WhatsApp test message: {str(e)}")
    app.run(debug=True, port=8000)
