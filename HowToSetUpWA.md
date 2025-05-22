# Gonna take a while. dont edit the code and use as it is only update deployment variables.
CODE WORKS FINE DONT TOUCH IT 

## 1. What u need

- [Google Cloud Platform](https://console.cloud.google.com/) account
- [Meta for Developers](https://developers.facebook.com/) account
- [Vercel](https://vercel.com/) account 
- AND GOD 

## 2. WhatsApp Business API Setup inorder to get message

1. **Create a Meta Developer Account**:
   - Go to [Meta for Developers](https://developers.facebook.com/)
   - Create a developer account if you don't have one
   - Log in to your account

2. **Create a Meta App**:
   - Click "Create App"
   - Select "Business" as the app type
   - Enter your app name and contact email
   - Click "Create App"

3. **Add WhatsApp to Your App**:
   - From your app dashboard, click "Add Products"
   - Select "WhatsApp" and click "Set Up"
   - In the WhatsApp panel, navigate to "Getting Started"

4. **Set Up WhatsApp Business Account**:
   - In the WhatsApp panel, follow the steps to create or link a WhatsApp Business Account
   - Select or create a Business Manager if prompted

5. **Get Your Phone Number**:
   - In the WhatsApp panel, go to "Configuration"
   - Add and verify a phone number to use with your app

6. **Get API Credentials**:
   - Go to "API Setup" in the WhatsApp panel
   - Note down your:
     - Phone Number ID
     - WhatsApp Business Account ID
     - Access Tokenx
a
7. **Set Up Webhook**:
   - In the WhatsApp panel, go to "Configuration" > "Webhooks"
   - Click "Edit"
   - Enter your webhook URL (your Vercel deployment URL + "/webhook")
   - Enter a verify token (PUT ONLY "BOT")
   - Subscribe to the messages

## 3. Google Calendar API Setup AND GEMINI 

1. **Create a New Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project

2. **Enable APIs**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API" and GEMINI API

3. **Create Service Account**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Enter a name, ID, and description for the service account
   - Click "Create and Continue"
   - Assign the "Editor" role and click "Continue"
   - Click "Done"

   * SAME WITH API KEY FOR GEMINI

4. **Generate Service Account Key**:
   - In the credentials page, click on your service account
   - Go to the "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON and click "Create"
   - Save the downloaded JSON file

5. **Share Your Google Calendar**:
   - Go to [Google Calendar](https://calendar.google.com/)
   - Find your calendar in the left sidebar
   - Click the three dots next to it and select "Settings and sharing"
   - Scroll to "Share with specific people"
   - Click "+ Add people"
   - Enter your service account email (found in the JSON file)
   - Set permission to "See all event details"
   - Click "Send"

6. **Get Your Calendar ID**:
   - In Calendar settings, scroll to "Integrate calendar"
   - Copy your Calendar ID (looks like an email address)

## 4. Deploy to Vercel

1. **Clone This Repository**:
   git clone https://github.com/Athiq21/Whatsapp_AI_Bot.git


2. **Set Up Environment Variables**:
   - In Vercel dashboard, go to your project settings
   - Add the following environment variables:
     - `WA_TOKEN`: Your WhatsApp API access token
     - `GEN_API`: Your Google Gemini API key
     - `PHONE_ID`: Your WhatsApp phone number ID
     - `PHONE_NUMBER`: Your WhatsApp phone number with country code (e.g., +1234567890)
     - `GOOGLE_CREDENTIALS`: The entire content of your service account JSON credentials file
     - `GOOGLE_CALENDAR_ID`: Your Google Calendar ID

3. **Deploy to Vercel**:
   - Push your code to GitHub
   - Connect your repository to Vercel
   - Configure the Build and Output settings
   - Deploy

## 5. IMPORTANT DONT SCREW THIS 

1. **Verify Webhook Connection**:
   - In the Meta Developer portal, complete the webhook setup by entering your deployed URL + "/webhook"
   - Use "BOT" as your verify token
   - Subscribe to the "messages" field


## 6. Features

- **AI Chat**: Ask questions and get responses powered by Google's Gemini AI
- **Calendar Integration**: Ask about your schedule and events
- **Automated Reminders**: Receive automatic hourly reminders about your daily schedule
- **Time-Based Queries**: Ask about specific days like today, tomorrow, or next Monday
- **Media Processing**: Send images, audio, or documents for AI analysis

IF U NEED SOMETHING TO MANAGE THEN MICROSERVICE THIS SHI and u done 
