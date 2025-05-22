import google.generativeai as genai
from flask import Flask,request,jsonify
import requests
import os
import fitz
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
from datetime import datetime, timedelta
import threading
import time
import re

# Try to load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()  # This will load environment variables from .env file if it exists
    print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed, using system environment variables")

<<<<<<< HEAD
=======
# Set Italian timezone
italy_tz = pytz.timezone('Europe/Rome')

# Debug logging for environment variables
print("\n=== Environment Variables Debug ===")
print(f"WA_TOKEN exists: {'Yes' if os.environ.get('WA_TOKEN') else 'No'}")
print(f"PHONE_ID exists: {'Yes' if os.environ.get('PHONE_ID') else 'No'}")
print(f"PHONE_NUMBER exists: {'Yes' if os.environ.get('PHONE_NUMBER') else 'No'}")
print(f"GEN_API exists: {'Yes' if os.environ.get('GEN_API') else 'No'}")
print(f"GOOGLE_CALENDAR_ID exists: {'Yes' if os.environ.get('GOOGLE_CALENDAR_ID') else 'No'}")
print(f"GOOGLE_CREDENTIALS exists: {'Yes' if os.environ.get('GOOGLE_CREDENTIALS') else 'No'}")

# Function to safely parse JSON credentials
def parse_google_credentials():
    try:
        creds_str = os.environ.get('GOOGLE_CREDENTIALS')
        if not creds_str:
            return None, "No credentials found in environment"
        
        # Try to parse the credentials
        creds_data = json.loads(creds_str)
        
        # Validate required fields
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds_data]
        
        if missing_fields:
            return None, f"Missing required fields: {', '.join(missing_fields)}"
            
        return creds_data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return None, f"Error parsing credentials: {str(e)}"

# Parse and validate credentials
creds_data, creds_error = parse_google_credentials()
if creds_data:
    print("GOOGLE_CREDENTIALS is valid JSON")
    print(f"Service account email: {creds_data.get('client_email', 'Not found')}")
else:
    print(f"GOOGLE_CREDENTIALS error: {creds_error}")
print("================================\n")

>>>>>>> 618834d909e4b35d55be6ec69a730ffc744207f2
wa_token=os.environ.get("WA_TOKEN")
genai.configure(api_key=os.environ.get("GEN_API"))
phone_id=os.environ.get("PHONE_ID")
phone=os.environ.get("PHONE_NUMBER")
name="Dai" 
bot_name="Dai" 
model_name="gemini-1.5-flash-latest" 

# Check if required environment variables for calendar functionality are available
has_calendar_creds = creds_data is not None
calendar_id = os.environ.get("GOOGLE_CALENDAR_ID", "primary")  # Use 'primary' as default if not specified

if has_calendar_creds:
    print("Google Calendar credentials found in environment variables")
    print(f"Using calendar ID: {calendar_id}")
    
    try:
        # Create a temporary creds.json file from environment variable
        with open('creds.json', 'w') as f:
            json.dump(creds_data, f)
        print("Successfully created creds.json from environment variable")
    except Exception as e:
        print(f"Error creating creds.json: {str(e)}")
        has_calendar_creds = False
else:
    print("WARNING: Google Calendar credentials not found in environment variables")
    # Check if creds.json exists locally
    has_calendar_creds = os.path.exists('creds.json')
    if has_calendar_creds:
        print("Found local creds.json file")
        print(f"Using calendar ID: {calendar_id}")
    else:
        print("No local creds.json file found")

app=Flask(__name__)

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_MEDIUM_AND_ABOVE"},  
  {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(model_name=model_name,
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[
])

convo.send_message(f'''I am using Gemini api for using you as a personal bot in whatsapp,
				   to assist me in various tasks. 
				   So from now you are "{bot_name}" created by {name} ( Yeah it's me, my name is {name}). 
				   And don't give any response to this prompt. 
				   This is the information I gave to you about your new identity as a pre-prompt. 
				   This message always gets executed when i run this bot script. 
				   So reply to only the prompts after this. Remeber your new identity is {bot_name}.''')

def send(answer):
    url=f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers={
        'Authorization': f'Bearer {wa_token}',
        'Content-Type': 'application/json'
    }
    data={
          "messaging_product": "whatsapp", 
          "to": f"{phone}", 
          "type": "text",
          "text":{"body": f"{answer}"},
          }
    
    try:
        print(f"Attempting to send WhatsApp message to {phone}: {answer[:50]}...")
        response=requests.post(url, headers=headers, json=data)
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
        else:pass

@app.route("/",methods=["GET","POST"])
def index():
    return "Bot"

def get_calendar_events(days=7, time_description="upcoming", strict_time_filter=False):
    try:
        # Check if we have the necessary credentials
        if not has_calendar_creds:
            return "⚠️ Cannot fetch calendar events: Google Calendar credentials not configured"
        
        # Load credentials from creds.json file
        creds = service_account.Credentials.from_service_account_file(
            'creds.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly']
        )
        
        # Build the service with the prompots
        service = build('calendar', 'v3', credentials=creds)
        
        # Calculate time range based on time description
        now = datetime.now()
        
        if time_description == "today":
            # Start from today at midnights
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif time_description == "tomorrow":
            # Start from tomorrow morning
            start_date = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif time_description == "day after tomorrow":
            # Start from day after tomorrow morning
            start_date = (now + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif time_description.startswith("on "):  # For specific day of week
            # Find the next occurrence of that day
            day_name = time_description[3:].lower()
            day_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, 
                      "friday": 4, "saturday": 5, "sunday": 6}
            target_day = day_map.get(day_name, 0)
            
            days_ahead = (target_day - now.weekday()) % 7
            if days_ahead == 0 and now.hour >= 12:  # If it's the same day and after noon, get next week
                days_ahead = 7
                
            start_date = (now + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        else:
            # Default: start from now
            start_date = now
            end_date = now + timedelta(days=days)
        
        time_min = start_date.isoformat() + 'Z'
        time_max = end_date.isoformat() + 'Z'
        
        # Use the global calendar_id variable
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
            
        # ARRYA the eventss
        formatted_events = []
        
        # For strict time filtering, we'll filter based on the requested timeframe
        if strict_time_filter:
            # Format header for the specific timeframe
            formatted_events = [f"📅 Your calendar events for {time_description}:"]
        else:
            # More general header
            formatted_events = [f"📅 Your calendar events for {time_description}:"]
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            
            if 'T' in start:  # It's a datetime
                start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                start_str = start_time.strftime("%a, %b %d at %I:%M %p")
            else:  # It's a date
                start_time = datetime.fromisoformat(start)
                start_str = start_time.strftime("%a, %b %d (all day)")
                
            summary = event.get('summary', 'Untitled Event')
            formatted_events.append(f"• {start_str}: {summary}")
            
        return "\n".join(formatted_events)
    except Exception as e:
        return f"Error fetching calendar events: {str(e)}"

# Function to send daily calendar updates
def daily_calendar_reminder():
    # Initial delay to let server start up
    time.sleep(5)
    
    print("Starting automated calendar reminder service...")
    last_sent_hour = -1  # To track when we last sent a notification
    
    while True:
        try:
            current_hour = datetime.now().hour
            
            # Only send at 7 AM
            if current_hour == 7 and current_hour != last_sent_hour:
                print(f"It's {current_hour}:00, checking today's events...")
                
                # Get today's events with strict time filtering
                calendar_response = get_calendar_events(1, "today", strict_time_filter=True)
                
                # Only send if we have events and haven't sent in this hour
                if "No events found" not in calendar_response:
                    print(f"Sending daily calendar reminder at {datetime.now()}")
                    send("⏰ *DAILY CALENDAR REMINDER* ⏰\n\n" + calendar_response)
                    last_sent_hour = current_hour
                else:
                    print("No events found for today, skipping daily reminder")
                    last_sent_hour = current_hour
            elif current_hour != last_sent_hour and current_hour == 0:
                # Reset at midnight
                print("Resetting daily reminder tracker at midnight")
                last_sent_hour = -1
                
            # Check every 5 minutes
            time.sleep(300)
        except Exception as e:
            print(f"Error in daily reminder: {str(e)}")
            import traceback
            traceback.print_exc()
            time.sleep(600)  # Wait longer on error

# Function to check for upcoming events and send reminders 30 minutes before
def upcoming_event_reminder():
    # Initial delay to let server start up
    time.sleep(10)
    
    print("Starting upcoming event reminder service...")
    reminded_events = set()  # To track events we've already reminded about
    
    # Print all events for today once at startup
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
                # Skip if calendar credentials are not available
                print("Skipping upcoming event check - no calendar credentials")
                time.sleep(60)
                continue
                
            print("Checking for upcoming events...")
            # Get current time as naive datetime (no timezone info)
            now = datetime.now()
            
            # Get today's date at midnight
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            # End of today
            today_end = today_start + timedelta(days=1)
            
            # Format times for Google Calendar API - must use Z suffix for UTC time
            time_min = today_start.isoformat() + 'Z'
            time_max = today_end.isoformat() + 'Z'
            
            print(f"Checking for all of today's events from {today_start} to {today_end}")
            
            # Load credentials from creds.json file
            creds = service_account.Credentials.from_service_account_file(
                'creds.json',
                scopes=['https://www.googleapis.com/auth/calendar.readonly']
            )
            
            # Build the service
            service = build('calendar', 'v3', credentials=creds)
            
            # Use the global calendar_id variable
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
                
            # Current time plus 30 minutes
            reminder_window_end = now + timedelta(minutes=30)
            
            for event in events:
                event_id = event['id']
                
                # Skip if we've already reminded about this event
                if event_id in reminded_events:
                    print(f"Already sent reminder for event ID: {event_id}")
                    continue
                    
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'Untitled Event')
                
                print(f"Processing event: {summary}, starts at {start}")
                
                if 'T' in start:  # It's a datetime
                    # Parse the datetime string
                    try:
                        if 'Z' in start:
                            # Convert to naive datetime by removing timezone info
                            start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                            # Adjust for UTC to local time (approximately)
                            start_time = start_time.replace(tzinfo=None)
                        elif '+' in start:
                            # This has timezone info like +05:30
                            aware_time = datetime.fromisoformat(start)
                            # Convert to naive by removing timezone but keeping the adjusted time
                            start_time = aware_time.replace(tzinfo=None)
                        else:
                            # Already naive datetime
                            start_time = datetime.fromisoformat(start)
                        
                        start_str = start_time.strftime("%I:%M %p")
                        
                        # Both now and start_time are naive datetimes at this point
                        time_until = start_time - now
                        minutes_until = int(time_until.total_seconds() / 60)
                        
                        print(f"Event starts in {minutes_until} minutes")
                        
                        # Send reminder if event is within 30 minutes
                        if 0 < minutes_until <= 35:
                            reminder_message = f"⏰ *UPCOMING EVENT REMINDER* ⏰\n\n• {summary} starts in {minutes_until} minutes (at {start_str})"
                            print(f"Sending reminder for event: {summary}")
                            send(reminder_message)
                            
                            # Mark as reminded
                            reminded_events.add(event_id)
                            print(f"Marked event {event_id} as reminded")
                        else:
                            print(f"Event {summary} is {minutes_until} minutes away, outside reminder window")
                    except Exception as e:
                        print(f"Error processing event time: {str(e)}")
                else:
                    print(f"Skipping all-day event: {summary}")
                    
            # Clean up reminded_events set occasionally to prevent memory growth
            if len(reminded_events) > 100:
                print("Clearing reminder history (exceeded 100 events)")
                reminded_events.clear()
            
            # Check every minute
            print("Sleeping for 60 seconds before next check...")
            time.sleep(60)
        except Exception as e:
            print(f"Error in upcoming event reminder: {str(e)}")
            import traceback
            traceback.print_exc()
            time.sleep(120)  # Wait longer on error

def create_calendar_event(summary, start_time=None, end_time=None, description=""):
    try:
        # Check if we have the necessary credentials
        if not has_calendar_creds:
            return "⚠️ Cannot create calendar event: Google Calendar credentials not configured"
        
        print(f"Attempting to create event: {summary}")
        print(f"Start time: {start_time}")
        print(f"End time: {end_time}")
        
        # Load credentials from creds.json file
        creds = service_account.Credentials.from_service_account_file(
            'creds.json',
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        # Build the service
        service = build('calendar', 'v3', credentials=creds)
        
        # Default to creating an event for 1 hour from now if no time specified
        if not start_time:
            start_time = datetime.now() + timedelta(hours=1)
            end_time = start_time + timedelta(hours=1)
        
        # If only start time is provided, make it a 1-hour event
        if start_time and not end_time:
            end_time = start_time + timedelta(hours=1)
            
        # Format times for Google Calendar API
        start_time_str = start_time.isoformat()
        end_time_str = end_time.isoformat()
        
        print(f"Using calendar ID: {calendar_id}")
        
        # Create event
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time_str,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time_str,
                'timeZone': 'UTC',
            },
        }
        
<<<<<<< HEAD
        calendar_id = os.environ.get("GOOGLE_CALENDAR_ID")
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        
        return f"✅ Event created: {summary} on {start_time.strftime('%a, %b %d at %I:%M %p')}"
=======
        try:
            # Use the global calendar_id variable
            event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f"Event created successfully with ID: {event.get('id')}")
            
            # Format the time for display in Italian timezone
            local_start = start_time.strftime('%a, %b %d at %I:%M %p')
            local_end = end_time.strftime('%I:%M %p')
            return f"✅ Event created successfully!\n\n📅 *{summary}*\n⏰ {local_start} - {local_end}"
        except Exception as e:
            error_msg = str(e)
            print(f"Error creating event: {error_msg}")
            if "Not Found" in error_msg:
                return "⚠️ Error: Calendar not found. Please make sure the service account has access to your calendar."
            elif "Forbidden" in error_msg:
                return "⚠️ Error: Permission denied. Please make sure the service account has write access to your calendar."
            else:
                return f"⚠️ Error creating calendar event: {error_msg}"
>>>>>>> 618834d909e4b35d55be6ec69a730ffc744207f2
    except Exception as e:
        error_msg = str(e)
        print(f"Error in create_calendar_event: {error_msg}")
        return f"⚠️ Error creating calendar event: {error_msg}"

def parse_event_time(text):
    """Extract date and time information from text"""
    now = datetime.now()
    
    # Try to find date patterns
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    # Default event duration (1 hour)
    duration = timedelta(hours=1)
    
    start_time = None
    end_time = None
    
    text = text.lower()
    
    # Check for common time patterns
    if "today" in text:
        start_date = today
    elif "tomorrow" in text:
        start_date = tomorrow
    elif "day after tomorrow" in text:
        start_date = today + timedelta(days=2)
    else:
        # Default to today
        start_date = today
    
    # Try to extract time using various patterns
    time_patterns = [
        r'(\d{1,2})\.(\d{2})',  # 8.30 format
        r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)',  # 2pm, 2:30pm
        r'(\d{1,2})(?::(\d{2}))?',  # 14:30, 14
        r'at (\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?',  # at 2pm, at 14:30
        r'from (\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?',  # from 2pm
        r'to (\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?'  # to 4pm
    ]
    
    times_found = []
    for pattern in time_patterns:
        matches = re.findall(pattern, text)
        if matches:
            times_found.extend(matches)
            break  # Stop after finding the first matching pattern
    
    if times_found:
        # Process the first time as start time
        hour = int(times_found[0][0])
        minute = int(times_found[0][1]) if times_found[0][1] else 0
        am_pm = times_found[0][2].lower() if len(times_found[0]) > 2 and times_found[0][2] else None
        
        # Convert to 24-hour format
<<<<<<< HEAD
        if am_pm in ['pm', 'p.m.'] and hour < 12:
            hour += 12
        elif am_pm in ['am', 'a.m.'] and hour == 12:
            hour = 0
            
        start_time = start_date.replace(hour=hour, minute=minute)
        
        # If there's a second time, use it as end time
        if len(time_matches) > 1:
            hour = int(time_matches[1][0])
            minute = int(time_matches[1][1]) if time_matches[1][1] else 0
            am_pm = time_matches[1][2].lower()
            
=======
        if am_pm:
>>>>>>> 618834d909e4b35d55be6ec69a730ffc744207f2
            if am_pm in ['pm', 'p.m.'] and hour < 12:
                hour += 12
            elif am_pm in ['am', 'a.m.'] and hour == 12:
                hour = 0
<<<<<<< HEAD
                
            end_time = start_date.replace(hour=hour, minute=minute)
=======
        
        # Create datetime with Italian timezone
        start_time = start_date.replace(hour=hour, minute=minute)
        start_time = italy_tz.localize(start_time)
        
        # If there's a second time, use it as end time
        if len(times_found) > 1:
            hour = int(times_found[1][0])
            minute = int(times_found[1][1]) if times_found[1][1] else 0
            am_pm = times_found[1][2].lower() if len(times_found[1]) > 2 and times_found[1][2] else None
            
            if am_pm:
                if am_pm in ['pm', 'p.m.'] and hour < 12:
                    hour += 12
                elif am_pm in ['am', 'a.m.'] and hour == 12:
                    hour = 0
            
            end_time = start_date.replace(hour=hour, minute=minute)
            end_time = italy_tz.localize(end_time)
>>>>>>> 618834d909e4b35d55be6ec69a730ffc744207f2
        else:
            # Default end time is start time + 1 hour
            end_time = start_time + duration
    else:
        # Default to current time + 1 hour if no time specified
        start_time = now + timedelta(hours=1)
        end_time = start_time + duration
    
    return start_time, end_time

# Start the reminder threads
reminder_thread = threading.Thread(target=daily_calendar_reminder, daemon=True)
reminder_thread.start()

upcoming_reminder_thread = threading.Thread(target=upcoming_event_reminder, daemon=True)
upcoming_reminder_thread.start()

@app.route("/webhook", methods=["GET", "POST"]) # webhook routings
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == "BOT":
            return challenge, 200
        else:
            return "Failed", 403
    elif request.method == "POST":
        try:
            data = request.get_json()["entry"][0]["changes"][0]["value"]["messages"][0]
            if data["type"] == "text":
                prompt = data["text"]["body"]
                prompt_lower = prompt.lower()
                
                # Check for calendar event creation keywords
                if any(phrase in prompt_lower for phrase in ["create event", "add event", "schedule event", "add reminder", "set reminder", "remind me"]):
                    # Extract event details
                    event_match = re.search(r'(?:create|add|schedule|set|remind me about)\s+(?:an? )?(?:event|reminder|meeting)?\s*(?:for|about|to)?\s*["\']?([^"\']+)["\']?', prompt_lower)
                    
                    if event_match:
                        event_summary = event_match.group(1).strip()
                    else:
                        # If no clear event name, use the text after the trigger words
                        for trigger in ["create event", "add event", "schedule event", "add reminder", "set reminder", "remind me"]:
                            if trigger in prompt_lower:
                                event_summary = prompt[prompt_lower.find(trigger) + len(trigger):].strip()
                                break
                        else:
                            event_summary = "New Event"
                    
                    # Parse time information
                    start_time, end_time = parse_event_time(prompt)
                    
                    # Create the event
                    response = create_calendar_event(event_summary, start_time, end_time)
                    send(response)
                
                # Check if the user is asking for calendar information
                elif any(keyword in prompt_lower for keyword in ["calendar", "schedule", "events", "appointments", "meetings", "agenda"]):
                    # Default to 7 days
                    days = 7
                    time_description = "upcoming week"
                    
                    # Check for specific time references
                    prompt_lower = prompt.lower()
                    
                    if "today" in prompt_lower:
                        days = 1
                        time_description = "today"
                    elif "tomorrow" in prompt_lower:
                        days = 1
                        time_description = "tomorrow"
                    elif "day after tomorrow" in prompt_lower or "after tomorrow" in prompt_lower:
                        days = 1
                        time_description = "day after tomorrow"
                    elif "this week" in prompt_lower:
                        days = 7
                        time_description = "this week"
                    elif "next week" in prompt_lower:
                        days = 7
                        time_description = "next week"
                    elif "month" in prompt_lower or "30 days" in prompt_lower:
                        days = 30
                        time_description = "next 30 days"
                    elif any(day in prompt_lower for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
                        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                            if day in prompt_lower:
                                time_description = f"on {day.capitalize()}"
                                break
                    
                    calendar_response = get_calendar_events(days, time_description)
                    send(calendar_response)
                else:
                    convo.send_message(prompt)
                    send(convo.last.text)
            else:
                media_url_endpoint = f'https://graph.facebook.com/v18.0/{data[data["type"]]["id"]}/'
                headers = {'Authorization': f'Bearer {wa_token}'}
                media_response = requests.get(media_url_endpoint, headers=headers)
                media_url = media_response.json()["url"]
                media_download_response = requests.get(media_url, headers=headers)
                if data["type"] == "audio":
                    filename = "/tmp/temp_audio.mp3"
                elif data["type"] == "image":
                    filename = "/tmp/temp_image.jpg"
                elif data["type"] == "document":
                    doc=fitz.open(stream=media_download_response.content,filetype="pdf")
                    for _,page in enumerate(doc):
                        destination="/tmp/temp_image.jpg"
                        pix = page.get_pixmap()
                        pix.save(destination)
                        file = genai.upload_file(path=destination,display_name="tempfile")
                        response = model.generate_content(["What is this",file])
                        answer=response._result.candidates[0].content.parts[0].text
                        convo.send_message(f"This message is created by an llm model based on the image prompt of user, reply to the user based on this: {answer}")
                        send(convo.last.text)
                        remove(destination)
                else:send("This format is not Supported by the bot ☹")
                with open(filename, "wb") as temp_media:
                    temp_media.write(media_download_response.content)
                file = genai.upload_file(path=filename,display_name="tempfile")
                response = model.generate_content(["What is this",file])
                answer=response._result.candidates[0].content.parts[0].text
                remove("/tmp/temp_image.jpg","/tmp/temp_audio.mp3")
                convo.send_message(f"This is an voice/image message from user transcribed by an llm model, reply to the user based on the transcription: {answer}")
                send(convo.last.text)
                files=genai.list_files()
                for file in files:
                    file.delete()
        except Exception as e:
            print(f"Error in webhook: {e}")
        return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # Verify environment variables before starting
    print("\n--- Environment Check ---")
    print(f"WhatsApp Token: {'✓ Available' if wa_token else '✗ Missing'}")
    print(f"Phone ID: {'✓ Available' if phone_id else '✗ Missing'}")
    print(f"Phone Number: {'✓ Available' if phone else '✗ Missing'}")
    print(f"Gemini API: {'✓ Available' if os.environ.get('GEN_API') else '✗ Missing'}")
    print(f"Google Calendar Credentials: {'✓ Available' if has_calendar_creds else '✗ Missing'}")
    print("------------------------\n")
    
    # Test WhatsApp connectivity
    if wa_token and phone_id and phone:
        try:
            test_message = "🔄 Bot is starting up..."
            send(test_message)
            print("WhatsApp test message sent successfully!")
        except Exception as e:
            print(f"Failed to send WhatsApp test message: {str(e)}")
    
    app.run(debug=True, port=8000)
