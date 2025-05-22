# WhatsApp AI Bot

A WhatsApp bot powered by Google's Gemini AI that can handle text messages, images, audio, and documents. It also includes calendar integration for managing events and reminders.

## Features

- 🤖 AI-powered responses using Google's Gemini
- 📅 Calendar integration for event management
- ⏰ Automated reminders and notifications
- 📷 Image and document analysis
- 🎵 Audio transcription
- 🔄 Real-time message handling

## Prerequisites

- Python 3.8 or higher
- WhatsApp Business API access
- Google Cloud Platform account
- Google Calendar API credentials
- Gemini API key

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
WA_TOKEN=your_whatsapp_token
PHONE_ID=your_phone_id
PHONE_NUMBER=your_phone_number
GEN_API=your_gemini_api_key
GOOGLE_CREDENTIALS=your_google_credentials_json
GOOGLE_CALENDAR_ID=your_calendar_id
```

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/whatsapp-ai-bot.git
cd whatsapp-ai-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Deployment on Vercel

1. Fork this repository
2. Create a new project on Vercel
3. Connect your GitHub repository
4. Add the required environment variables in Vercel's project settings
5. Deploy!

## Usage

1. Send a text message to your WhatsApp bot
2. For calendar events, use commands like:
   - "Create event Meeting at 2pm tomorrow"
   - "Show my calendar for today"
   - "What's on my schedule tomorrow?"
3. Send images or documents for AI analysis
4. Send voice messages for transcription

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 