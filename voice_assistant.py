import os
import json
import requests
import datetime
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googletrans import Translator
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging
import matplotlib.pyplot as plt
import numpy as np

# Load API Keys
load_dotenv()
BING_API_KEY = os.getenv("BING_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)
voices = engine.getProperty('voices')
for voice in voices:
    if "female" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
else:
    engine.setProperty('voice', voices[0].id)

# Initialize Sentiment Analyzer and Translator
analyzer = SentimentIntensityAnalyzer()
translator = Translator()
sentiment_history = []

# Logging Setup
logging.basicConfig(level=logging.INFO, filename='naina.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Reminder System
reminders_file = "reminders.json"
reminders = []

def save_reminders():
    try:
        with open(reminders_file, "w") as file:
            json.dump(reminders, file)
    except Exception as e:
        logging.error(f"Error saving reminders: {e}")

def load_reminders():
    global reminders
    if not os.path.exists(reminders_file):
        with open(reminders_file, "w") as file:
            json.dump([], file)
    try:
        with open(reminders_file, "r") as file:
            reminders = json.load(file)
    except Exception as e:
        logging.error(f"Error loading reminders: {e}")
        reminders = []

load_reminders()

# Google Calendar Setup
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
SERVICE_ACCOUNT_FILE = "config/credentials.json"
calendar_service = None
if os.path.exists(SERVICE_ACCOUNT_FILE):
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        calendar_service = build("calendar", "v3", credentials=creds)
    except Exception as e:
        logging.error(f"Google Calendar setup error: {e}")

# Speech Recognition
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        logging.info("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return "I didn't understand that."
        except sr.RequestError:
            return "Speech recognition service is unavailable."
        except sr.WaitTimeoutError:
            return "I didn't hear anything."

# Speak and Display Text
def respond(text):
    print(f"voice assitant: {text}")
    logging.info(f"voice assistant: {text}")
    engine.say(text)
    engine.runAndWait()

# AI Chat Response
def get_ai_response(prompt):
    try:
        response = model.start_chat().send_message(prompt)
        return response.text
    except Exception as e:
        logging.error(f"AI error: {e}")
        return "I encountered an error while processing your request."

# Weather
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        if response.get("main"):
            return f"Weather in {city}: {response['weather'][0]['description']}, {response['main']['temp']}°C"
        return "Could not fetch weather."
    except Exception as e:
        logging.error(f"Weather error: {e}")
        return "Weather service is unavailable."

# News
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url).json()
        articles = response.get("articles", [])[:5]
        return "\n".join([f"{a['title']} - {a['source']['name']}" for a in articles]) or "No news available."
    except Exception as e:
        logging.error(f"News error: {e}")
        return "News service is unavailable."

# Bing Search
def bing_search(query):
    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": 3}
    try:
        response = requests.get(url, headers=headers, params=params).json()
        return "\n".join([res['name'] for res in response.get('webPages', {}).get('value', [])])
    except Exception as e:
        logging.error(f"Bing search error: {e}")
        return "Search service is unavailable."

# Reminder
def add_reminder(task, time):
    reminders.append({"task": task, "time": time})
    save_reminders()
    return f"Reminder set for {task} at {time}"

def check_reminders():
    now = datetime.datetime.now()
    for reminder in reminders[:]:
        try:
            remind_time = datetime.datetime.strptime(reminder['time'], "%I:%M %p").replace(
                year=now.year, month=now.month, day=now.day)
            if now >= remind_time and abs((now - remind_time).total_seconds()) < 60:
                respond(f"Reminder: {reminder['task']}")
                reminders.remove(reminder)
                save_reminders()
        except Exception as e:
            logging.error(f"Reminder check error: {e}")

# Sentiment
def get_sentiment(text):
    scores = analyzer.polarity_scores(text)
    sentiment_history.append(scores['compound'])
    return scores

# Translate
def translate_text(text, dest_lang='es'):
    try:
        translated = translator.translate(text, dest=dest_lang)
        return translated.text
    except Exception as e:
        logging.error(f"Translate error: {e}")
        return "Translation error."

# Jokes
def get_joke():
    try:
        res = requests.get("https://official-joke-api.appspot.com/random_joke").json()
        return f"{res['setup']} - {res['punchline']}"
    except Exception as e:
        logging.error(f"Joke API error: {e}")
        return "Joke service is unavailable."

# Time
def get_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    return f"The time is {now}."

# Greeting
def greet_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning!"
    elif hour < 18:
        return "Good afternoon!"
    else:
        return "Good evening!"

# Calendar
def get_calendar_events():
    if not calendar_service:
        return "Google Calendar is not configured."
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    try:
        events_result = calendar_service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])
        return "Upcoming Events:\n" + "\n".join([e['summary'] for e in events]) if events else "No upcoming events."
    except Exception as e:
        logging.error(f"Calendar error: {e}")
        return "Error accessing calendar."

# Plots
def plot_sentiment():
    if not sentiment_history:
        return "No sentiment data to plot yet."
    plt.step(range(len(sentiment_history)), sentiment_history, where='post', label='Sentiment')
    plt.title('Sentiment Over Time')
    plt.xlabel('Interaction')
    plt.ylabel('Sentiment Score')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.show()
    return "Sentiment plot displayed."

# Basic Queries
def respond_to_basic_queries(user_input):
    if "how are you" in user_input:
        return "I'm fine, thank you! How can I assist you?"
    elif "your name" in user_input:
        return "I am your voice assistant, Naina."
    elif "who are you" in user_input:
        return "I am Naina, your AI-powered voice assistant."
    elif "what can you do" in user_input:
        return "I can help with weather, news, reminders, jokes, translations, and more."
    return None

# Main
if __name__ == "__main__":
    respond(f"{greet_user()} I'm your voice assistant. How can I help you?")

    while True:
        user_input = listen().strip()
        print(f"You: {user_input}")
        logging.info(f"You: {user_input}")

        if "exit" in user_input or "bye" in user_input:
            respond("Goodbye! Have a great day.")
            break

        check_reminders()

        basic_response = respond_to_basic_queries(user_input)
        if basic_response:
            respond(basic_response)
            continue

        if "weather in" in user_input:
            city = user_input.split("weather in")[-1].strip()
            response = get_weather(city)
        elif "news" in user_input:
            response = get_news()
        elif "search for" in user_input:
            query = user_input.replace("search for", "").strip()
            response = bing_search(query)
        elif "set reminder" in user_input:
            parts = user_input.replace("set reminder ", "").split(" at ")
            response = add_reminder(parts[0], parts[1]) if len(parts) == 2 else "Please specify time (e.g., 6 PM)."
        elif "translate to" in user_input:
            parts = user_input.split()
            dest_lang = parts[-1]
            text_to_translate = " ".join(parts[2:-2])
            response = translate_text(text_to_translate, dest_lang)
        elif "joke" in user_input:
            response = get_joke()
        elif "calendar" in user_input:
            response = get_calendar_events()
        elif "time" in user_input:
            response = get_time()
        elif "plot sentiment" in user_input:
            response = plot_sentiment()
        else:
            response = get_ai_response(user_input)

        sentiment = get_sentiment(user_input)
        logging.info(f"Sentiment: {sentiment}")
        respond(response)
