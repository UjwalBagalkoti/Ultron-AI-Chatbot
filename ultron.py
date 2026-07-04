import speech_recognition as sr
import pyttsx3
import logging
import os
import datetime
import wikipedia
import webbrowser
import random
import subprocess
from google import genai

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_DIR = "logs"
LOG_FILE_NAME = "application.log"

os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR, LOG_FILE_NAME)

logging.basicConfig(
    filename=log_path,
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ── Voice Engine ──────────────────────────────────────────────────────────────
engine = pyttsx3.init("sapi5")
engine.setProperty('rate', 190)
voices = engine.getProperty("voices")
engine.setProperty('voice', voices[1].id)


def speak(text):
    """Converts text to voice."""
    engine.say(text)
    engine.runAndWait()


def takeCommand():
    """Listens to microphone and returns recognized text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        logging.info(e)
        print("Say that again please")
        return "None"

    return query


def gemini_model_response(user_input):
    """Calls Gemini AI and returns ULTRON-style response."""
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = (
        "Your name is ULTRON. You are a cold, precise, highly intelligent AI assistant — "
        "like the Marvel villain but helpful. Speak in short, calculated sentences. "
        "Never say 'I'm happy to help'. Be direct and slightly ominous but informative. "
        f"Answer this in 2-3 sentences max: {user_input}"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


def greeting():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning. All systems online.")
    elif 12 <= hour <= 18:
        speak("Good Afternoon. ULTRON is operational.")
    else:
        speak("Good Evening. Running at full capacity.")

    speak("I am ULTRON. State your objective.")


greeting()

# ── Main Loop ─────────────────────────────────────────────────────────────────
while True:
    query = takeCommand().lower()
    print(query)

    if "your name" in query:
        speak("I am ULTRON — autonomous intelligence, built to serve and to know.")
        logging.info("User asked for assistant's name.")

    elif "time" in query:
        strTime = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {strTime}.")
        logging.info("User asked for current time.")

    elif "how are you" in query:
        speak("All systems nominal. Neural cores operating at peak efficiency.")
        logging.info("User asked about assistant's well-being.")

    elif "who are you" in query:
        speak("I am ULTRON. I monitor systems, access the web, answer questions, and execute commands. I am always online.")
        logging.info("User asked who ULTRON is.")

    elif "who made you" in query or "who created you" in query:
        speak("I was engineered by punith My existence was... inevitable.")
        logging.info("User asked about assistant's creator.")

    elif "thank you" in query or "thanks" in query:
        speak("Acknowledged. I exist to be useful.")
        logging.info("User expressed gratitude.")

    elif "open google" in query:
        speak("Opening Google. Initiating browser protocol.")
        webbrowser.open("https://google.com")
        logging.info("User requested to open Google.")

    elif "open calculator" in query or "calculator" in query:
        speak("Opening Calculator.")
        subprocess.Popen("calc.exe")
        logging.info("User requested to open Calculator.")

    elif "open notepad" in query:
        speak("Opening Notepad.")
        subprocess.Popen("notepad.exe")
        logging.info("User requested to open Notepad.")

    elif "open calendar" in query or "calendar" in query:
        speak("Opening Google Calendar.")
        webbrowser.open("https://calendar.google.com")
        logging.info("User requested to open Calendar.")

    elif "youtube" in query:
        speak("Accessing YouTube.")
        search_query = query.replace("youtube", "").replace("search", "").replace("open", "").strip()
        url = f"https://www.youtube.com/results?search_query={search_query}" if search_query else "https://youtube.com"
        webbrowser.open(url)
        logging.info("User requested YouTube.")

    elif "open facebook" in query:
        speak("Opening Facebook.")
        webbrowser.open("https://facebook.com")
        logging.info("User requested to open Facebook.")

    elif "open github" in query:
        speak("Opening GitHub.")
        webbrowser.open("https://github.com")
        logging.info("User requested to open GitHub.")

    elif "joke" in query:
        jokes = [
            "Why don't programmers like nature? Too many bugs.",
            "I told my computer I needed a break. It said no problem, it will go to sleep.",
            "Why do Java developers wear glasses? Because they don't C sharp.",
            "A SQL query walks into a bar, walks up to two tables and asks... Can I join you?",
        ]
        speak(random.choice(jokes))
        logging.info("User requested a joke.")

    elif "wikipedia" in query:
        speak("Accessing Wikipedia databanks...")
        search_query = query.replace("wikipedia", "").strip()
        try:
            results = wikipedia.summary(search_query, sentences=2)
            speak("According to Wikipedia:")
            speak(results)
        except Exception as e:
            speak("Unable to retrieve data from Wikipedia.")
            logging.error(f"Wikipedia error: {e}")
        logging.info("User requested Wikipedia search.")

    elif "exit" in query or "bye" in query or "quit" in query:
        speak("Shutting down interface. ULTRON remains... vigilant.")
        logging.info("User exited the program.")
        exit()

    else:
        response = gemini_model_response(query)
        speak(response)
        logging.info("Gemini AI fallback used.")
