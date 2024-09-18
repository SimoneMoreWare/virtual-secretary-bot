# virtual-secretary-bot
**Virtual Secretary - Automated Response Bot** is a Python-based application designed to automatically respond to messages on Telegram based on your availability in Google Calendar. This bot helps you manage communications efficiently when you're busy, by checking your schedule and replying with your availability.

## Features
- Automatically responds to Telegram messages.
- Checks availability from Google Calendar.
- Translates natural language time queries to English.
- Parses and interprets human-readable date/time strings.
- Provides event details based on the extracted date/time from messages.

## Documentation

- **Google Calendar API Quickstart for Python**:
  Learn how to set up and use the Google Calendar API with Python.
  [Google Calendar API Quickstart](https://developers.google.com/calendar/api/quickstart/python?hl=en)

- **Parsing Human-Readable Date/Time Strings**:
  Use the `parsedatetime` library to parse date and time strings.
  [Parsedatetime Library](https://github.com/bear/parsedatetime)

- **Google Translate API**:
  Guide on using Google Translate for translating text in Python.
  [Google Translate in Python](https://lokalise.com/blog/how-to-translate-languages-in-python-with-google-translate-and-deepl-plus-more/)

- **Telethon for Telegram Userbot**:
  Official documentation and GitHub repository for Telethon, the library used to interact with Telegram.
  [Telethon Documentation](https://docs.telethon.dev/en/stable/)
  [Telethon GitHub Repository](https://github.com/LonamiWebs/Telethon)

- **Google Calendar Automation in Python**:
  A video tutorial on automating Google Calendar with Python.
  [Google Calendar Automation Video](https://www.youtube.com/watch?v=B2E82UPUnOY)

## Why Telethon?

We chose **Telethon** for this project because it stands out as one of the few libraries that support the creation of userbots in Telegram. Unlike other libraries like `python-telegram-bot` or `aiogram`, which are primarily designed for creating bots that interact with Telegram's Bot API, Telethon allows us to interact with Telegram as a regular user. This capability is crucial for our use case, where the bot needs to respond to messages in a personal user context, not just within bot channels or groups. Telethon provides robust functionality for managing user interactions and accessing Telegram's full range of features, making it an ideal choice for implementing a userbot that integrates seamlessly with Google Calendar and other services.

## Installation

To set up this bot, follow these steps:

1. **Clone the Repository**:
   ```
   git clone https://github.com/yourusername/virtual-secretary.git
   cd virtual-secretary
   ```

2. **Create a Virtual Environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Obtain API Credentials**:
    * Telegram API: Obtain your api_id and api_hash from Telegram [here](https://core.telegram.org/api/obtaining_api_id).
    * Google Calendar API: Follow the [quickstart guide](https://developers.google.com/calendar/api/quickstart/python?hl=en) to get your credentials.json.

5. **Configure Your Credentials**:
    * Replace the placeholder values in the script with your actual Telegram API credentials and Google Calendar credentials.
    * Ensure you have a credentials.json file for Google Calendar and a token.json file if you've previously authenticated.

## Usage
1. **Start the bot**
   ```
   python main.py
   ```
   
2. **Interact with the Bot**:
    * The bot will listen for incoming messages on Telegram.
    * It will automatically check your Google Calendar for availability and respond based on the extracted date/time from messages.

## Configuration
* Telegram Credentials:
     * Set api_id, api_hash, and phone_number in the script.
* Google Calendar API:
     * Ensure credentials.json is present in the project directory.
* User ID:
     * Set yourUser_id to your Telegram user ID.

## Contributing
Feel free to fork the repository, create branches, and submit pull requests. Contributions to improve functionality or documentation are welcome.

## License
This project is licensed under the MIT License. See the [LICENSE](https://opensource.org/license/mit) file for details.

## Contact
For questions or issues, please open an issue on the GitHub repository or contact me at candidosimone598@gmail.com.


### Notes:
- **Replace placeholders** like `yourusername`, `your-email@example.com`, and other project-specific details with actual values.
- **Include a `requirements.txt` file** with all the necessary dependencies for the project.
- **Update URLs and other references** as needed.

This `README.md` provides a comprehensive guide to understanding, installing, and using your bot, while also directing users to relevant resources for further information.
