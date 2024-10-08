import datetime
import os.path

import parsedatetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser
from googletrans import Translator

# Scope for read-only access to the Google Calendar API.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Insert your Telegram credentials
api_id = 'YOUR_API_ID'  # Replace with your actual API ID
api_hash = 'YOUR_API_HASH'  # Replace with your actual API hash
your_user_id = 'YOUR_USER_ID'  # Replace with your Telegram user ID
phone_number = 'YOUR_PHONE_NUMBER'  # Replace with your phone number in international format (e.g., '+1234567890')
max_results = 10
your_name = "Simone"

# Global variable to track when the bot last responded
last_response_time = 0
response_cooldown = 60  # Set cooldown period (in seconds)

# List of calendar IDs to retrieve events from
CALENDAR_IDS = [
    'primary',  # Primary calendar
    'id1_otherCalendar',  # Example calendar ID
    'id2_otherCalendar',
    'id3_otherCalendar',
    'id4_otherCalendar'
]


# Create a new Telegram client instance
client = TelegramClient('session_name', api_id, api_hash)

# Create an instance of the parsedatetime parser
cal = parsedatetime.Calendar()

def load_credentials() -> Credentials:
    """
    Load the user's credentials from token.json if available.

    Returns:
        Credentials object or None if credentials are not available or invalid.
    """
    if os.path.exists("token.json"):
        return Credentials.from_authorized_user_file("token.json", SCOPES)
    return None

def save_credentials(creds: Credentials):
    """
    Save the user's credentials to token.json for future use.

    Args:
        creds: The Credentials object to save.
    """
    with open("token.json", "w") as token:
        token.write(creds.to_json())

def get_authenticated_service() -> build:
    """
    Authenticate the user and return an authorized Google Calendar API service.

    Returns:
        Google Calendar API service object
    """
    creds = load_credentials()

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=51306)
        save_credentials(creds)
    
    return build("calendar", "v3", credentials=creds)

def translate_time_string(time_string: str) -> str:
    """
    Translate the time string to English using Google Translate.

    Args:
        time_string: The natural language time string to translate.

    Returns:
        Translated time string in English or the original string if translation fails.
    """
    translator = Translator()
    try:
        translated_time_string = translator.translate(time_string, src='auto', dest='en').text
        return translated_time_string
    except Exception as e:
        return time_string

def parse_time_string(time_string: str) -> tuple:
    """
    Parse the translated time string into a datetime object.

    Args:
        time_string: The translated time string to parse.

    Returns:
        Tuple containing parsed datetime object (or None) and flag_now (boolean).
    """
    if not time_string:
        return None, False  # Return False if there is no valid time_string

    try:
        
        # Use parsedatetime to parse the time string
        time_struct, parse_status = cal.parse(time_string)
        
        if "now" in time_string.lower():
            parse_status = 1
            flag_now = True
        else: 
            flag_now = False
                    
        if parse_status == 0:
            
            # If parsing fails, return None and False
            return None, False
        
        if time_struct:
            
            # Convert the time structure into a datetime object
            return datetime.datetime(*time_struct[:6]), flag_now
        
        return None, False
    
    except Exception as e:
        return None, False

def get_events_by_time(service, calendar_id, time_string) -> list:
    """
    Retrieve events from a specified calendar based on a natural language time string.

    Args:
        service: The authenticated Google Calendar API service object.
        calendar_id: The ID of the calendar to retrieve events from.
        time_string: The natural language time string to use for retrieving events.

    Returns:
        List of events from the Google Calendar API or an empty list if an error occurs.
    """
    now = datetime.datetime.utcnow()

    # Translate and parse the time string
    translated_time_string = translate_time_string(time_string)
    parsed_time, flag_now = parse_time_string(translated_time_string)  # Also get flag_now

    if not parsed_time:
        return []

    # Extract only the date
    date_only = parsed_time.date()

    # Set time_min and time_max
    if flag_now:
        time_min = datetime.datetime.utcnow().isoformat() + "Z"
        time_max = (datetime.datetime.utcnow() + datetime.timedelta(minutes=90)).isoformat() + "Z"
    else:
        time_min = datetime.datetime.combine(date_only, datetime.time.min).isoformat() + "Z"
        time_max = datetime.datetime.combine(date_only, datetime.time(23, 59, 59)).isoformat() + "Z"
    
    try:
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        # Filter events that belong only to the current day
        filtered_events = []
        for event in events:
            start_date_str = event["start"].get("dateTime", event["start"].get("date"))
            start_date = datetime.datetime.strptime(start_date_str[:10], "%Y-%m-%d").date()
            if start_date == date_only:
                filtered_events.append(event)
        
        return filtered_events

    except HttpError as error:
        return []

def format_events(events) -> str:
    """
    Format the list of events into a human-readable string.

    Args:
        events: List of events to format.

    Returns:
        Formatted string of event details or a message indicating no events were found.
    """
    if not events:
        return "No upcoming events found."
    event_details = []
    event_details.append("Hi, I am " + your_name + "'s virtual assistant, I will list his schedule:\n")
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        event_details.append(f"{start} - {event['summary']}")
    return "\n".join(event_details)

def extract_dates_from_message(message: str) -> tuple:
    """
    Extract date from the message text.

    Args:
        message: The message text to analyze.

    Returns:
        Extracted datetime object or None if extraction fails.
    """
    # Translate the message to English
    translated_message = translate_time_string(message)

    # Parse the translated message to extract date
    parsed_date = parse_time_string(translated_message)
    
    return parsed_date

def check_current_events(service, calendar_ids) -> bool:
    """
    Check if there are any events happening at the current time across specified calendars.

    Args:
        service: The authenticated Google Calendar API service object.
        calendar_ids: List of calendar IDs to check for events.

    Returns:
        True if there is a current event, otherwise False.
    """
    now = datetime.datetime.utcnow().isoformat() + "Z"  # Current time in UTC

    for calendar_id in calendar_ids:
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=now,
                timeMax=(datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).isoformat() + "Z",
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        
        if events:
            return True  # There is at least one current event
    
    return False  # No current events found


def get_current_event(service, calendar_ids):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId=calendar_ids[0], timeMin=now, maxResults=1, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events[0] if events else None

async def is_user_online(user_id) -> bool:
    """
    Checks if the user is online on Telegram.

    Args:
        user_id: The Telegram user ID to check.

    Returns:
        True if the user is online, False otherwise.
    """
    user = await client.get_entity(user_id)
    return getattr(user.status, 'was_online', None) is None  # True if the user is online


@client.on(events.NewMessage)
async def handle_new_message(event):
    global last_response_time
    
    # Check if the message comes from a private chat
    if isinstance(event.message.peer_id, PeerUser):
        
        # Access the text of the message
        message_text = event.message.text
        
        # Extract the user ID from the message
        user_id = event.message.from_id.user_id if event.message.from_id else None
        
        # Check if the user ID is different and if a date was extracted
        isNot_same_user = (your_user_id != user_id)
        
        # Get the authenticated Google Calendar service
        service = get_authenticated_service()
       
        # Extract the date from the message text
        extracted_date = extract_dates_from_message(message_text)
        
        current_time = datetime.datetime.utcnow().timestamp()
        
        if extracted_date[0] is not None and isNot_same_user:
            # Handle events...
            all_events = []
            for calendar_id in CALENDAR_IDS:
                events = get_events_by_time(service, calendar_id, message_text)
                all_events.extend(events)

            # Sort all events by start time and take the first max_results events
            all_events.sort(key=lambda e: e["start"].get("dateTime", e["start"].get("date")))
            limited_events = all_events[:max_results]  # Adjust max results as needed
            
            if not all_events:
                await event.reply("Hi, I am " + your_name + "'s virtual assistant, I will list his schedule. He does not currently have any commitments on his schedule.")
                
            
            if limited_events:
                response = format_events(limited_events)
                await event.reply(response)
                
        else:
            # Check if there are current events
            if check_current_events(service, CALENDAR_IDS) and isNot_same_user:
                if await is_user_online(your_user_id):
                    return  # Do nothing if the user is online

                current_event = get_current_event(service, CALENDAR_IDS)
                end_time = current_event["end"].get("dateTime", current_event["end"].get("date"))
                end_time_only = end_time[11:16]
                
                # Check if enough time has passed since the last response
                if current_time - last_response_time >= response_cooldown:
                    await event.reply(f"Hi, I am {your_name}'s virtual assistant. He's currently busy with another event, but he will be free after {end_time_only}.")
                    last_response_time = current_time  # Update last response time
                return
    else:
        # Do nothing if the message comes from a group
        pass

def main():
    """
    Main function to start the Telegram client and keep it running.
    """
    
    # Authenticate and get the Google Calendar service
    service = get_authenticated_service()
        
    # Start the Telegram client using the provided phone number
    client.start(phone_number)
    
    # Keep the bot running until it is disconnected
    client.run_until_disconnected()

if __name__ == "__main__":
    main()
