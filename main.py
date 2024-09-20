import datetime
import os.path
import parsedatetime
from googletrans import Translator
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser  # Import to identify private chats

# Scope for read-only access to the Google Calendar API.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Insert your Telegram credentials
api_id = 'YOUR_API_ID'  # Replace with your actual API ID
api_hash = 'YOUR_API_HASH'  # Replace with your actual API hash
yourUser_id = 'YOUR_USER_ID'  # Replace with your Telegram user ID
phone_number = 'YOUR_PHONE_NUMBER'  # Replace with your phone number in international format (e.g., '+1234567890')
max_results = 10
your_name = "Simone"

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

def load_credentials():
    """
    Load the user's credentials from token.json if available.

    Returns:
        Credentials object or None if credentials are not available or invalid.
    """
    if os.path.exists("token.json"):
        return Credentials.from_authorized_user_file("token.json", SCOPES)
    return None

def save_credentials(creds):
    """
    Save the user's credentials to token.json for future use.

    Args:
        creds: The Credentials object to save.
    """
    with open("token.json", "w") as token:
        token.write(creds.to_json())

def get_authenticated_service():
    """
    Authenticate the user and return an authorized Google Calendar API service.

    Returns:
        Google Calendar API service object
    """
    creds = load_credentials()
    print(f"Loaded credentials: {creds}")

    if not creds or not creds.valid:
        print("Credentials not valid, refreshing or creating new ones...")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Credentials refreshed successfully.")
        else:
            print("Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=51306)
            print("OAuth flow completed, credentials obtained.")
        save_credentials(creds)
        print("Credentials saved.")
    
    return build("calendar", "v3", credentials=creds)

def translate_time_string(time_string):
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
        print(f"Translation error: {e}")
        return time_string

def parse_time_string(time_string):
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

def get_events_by_time(service, calendar_id, time_string):
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
    print(f"Translated time string: {translated_time_string}")
    parsed_time, flag_now = parse_time_string(translated_time_string)  # Also get flag_now

    if not parsed_time:
        return []

    print("Parsed_time: ", parsed_time)
    print("FlagNow:", flag_now)

    # Extract only the date
    date_only = parsed_time.date()

    # Set time_min and time_max
    if flag_now:
        time_min = datetime.datetime.utcnow().isoformat() + "Z"
        time_max = (datetime.datetime.utcnow() + datetime.timedelta(minutes=90)).isoformat() + "Z"
    else:
        time_min = datetime.datetime.combine(date_only, datetime.time.min).isoformat() + "Z"
        time_max = datetime.datetime.combine(date_only, datetime.time(23, 59, 59)).isoformat() + "Z"

    print("time_min: ", time_min)
    print("time_max: ", time_max)
    
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
        print(f"An error occurred: {error}")
        return []

def format_events(events):
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

def extract_dates_from_message(message):
    """
    Extract date from the message text.

    Args:
        message: The message text to analyze.

    Returns:
        Extracted datetime object or None if extraction fails.
    """
    # Translate the message to English
    translated_message = translate_time_string(message)
    print(f"Translated message: {translated_message}")

    # Parse the translated message to extract date
    parsed_date = parse_time_string(translated_message)
    if parsed_date:
        print(f"Extracted date: {parsed_date}")
    else:
        print(f"No date extracted from message: '{message}'")
    return parsed_date

def check_current_events(service, calendar_ids):
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


@client.on(events.NewMessage)
async def handle_new_message(event):
    """
    Handle incoming messages from Telegram and respond with calendar events.
    This handler only responds to messages from private chats, not groups.

    Args:
        event: The Telegram event containing the new message.
    """
    # Check if the message comes from a private chat
    if isinstance(event.message.peer_id, PeerUser):
        # Access the text of the message
        message_text = event.message.text
        
        # Extract the user ID from the message
        user_id = event.message.from_id.user_id if event.message.from_id else None
        
        # Check if the user ID is different and if a date was extracted
        isNot_same_user = (yourUser_id != user_id)
        
        # Log user ID for debugging
        print(user_id, yourUser_id)
        
        # Get the authenticated Google Calendar service
        service = get_authenticated_service()
       
        # Extract the date from the message text
        extracted_date = extract_dates_from_message(message_text)
        #here i want to add a function check if i have event in my calendar in a current time , if i am busy i send custom message
        
        if extracted_date[0] is not None and isNot_same_user:
            
            # Retrieve events from all specified calendars
            all_events = []
            for calendar_id in CALENDAR_IDS:
                events = get_events_by_time(service, calendar_id, message_text)
                all_events.extend(events)
            print("allEvent: ",all_events)
            # Sort all events by start time and take the first max_results events
            all_events.sort(key=lambda e: e["start"].get("dateTime", e["start"].get("date")))
            limited_events = all_events[:max_results]  # Adjust 5 as needed for max results
            
            if not all_events:
                await event.reply("Hi, I am " + your_name +"'s virtual assistant, I will list his schedule. He does not currently have any commitments on his schedule.")
            
            if limited_events:
                # Format the events into a response string
                response = format_events(limited_events)
                # Reply to the message with event details
                await event.reply(response)
        else:
            # Do not reply if no date was found or if the message is from the same user
            # Check if there are current events
            if check_current_events(service, CALENDAR_IDS):
                await event.reply("Hi, I am " + your_name +"'s virtual assistant. He's currently busy with another event. Please check back later.")
                return  # Exit the function if busy
            pass
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
    print("Userbot is running...")
    
    # Keep the bot running until it is disconnected
    client.run_until_disconnected()

if __name__ == "__main__":
    main()
