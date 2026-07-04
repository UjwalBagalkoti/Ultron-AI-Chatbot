from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import datetime
import wikipedia
import webbrowser
import random
import subprocess
import os
import platform
import psutil
import requests
import logging
from google import genai
from dotenv import load_dotenv
load_dotenv()  

app = Flask(__name__)
CORS(app)

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "application.log"),
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ── Gemini ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def gemini_response(user_input: str) -> str:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            "Your name is ULTRON. You are a cold, precise, highly intelligent AI assistant — like the Marvel villain but helpful. "
            "Speak in short, calculated sentences. Never say 'I'm happy to help'. Be direct and slightly ominous but informative. "
            f"Answer this in 2-3 sentences max: {user_input}"
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        return "I'm having trouble connecting to my AI brain right now. Please try again."


# ── Helper utilities ──────────────────────────────────────────────────────────
JOKES = [
    "Why don't programmers like nature? Too many bugs.",
    "I told my computer I needed a break. It said no problem, it will go to sleep.",
    "Why do Java developers wear glasses? Because they don't C sharp.",
    "How many programmers does it take to change a light bulb? None — it's a hardware problem.",
    "Why was the JavaScript developer sad? Because he didn't know how to 'null' his feelings.",
    "A SQL query walks into a bar, walks up to two tables and asks... Can I join you?",
]

QUOTES = [
    "The only way to do great work is to love what you do. – Steve Jobs",
    "Innovation distinguishes between a leader and a follower. – Steve Jobs",
    "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
    "It does not matter how slowly you go as long as you do not stop. – Confucius",
    "Life is what happens when you're busy making other plans. – John Lennon",
]

def get_greeting() -> str:
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 18:
        return "Good Afternoon"
    return "Good Evening"


def get_weather(city: str = "Bengaluru") -> str:
    try:
        url = f"https://wttr.in/{city}?format=3"
        resp = requests.get(url, timeout=5)
        return resp.text.strip() if resp.ok else f"Couldn't fetch weather for {city}."
    except Exception:
        return "Weather service is unavailable right now."


def get_system_info() -> dict:
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = str(datetime.datetime.now() - boot_time).split(".")[0]
    return {
        "cpu": f"{cpu}%",
        "ram_used": f"{ram.used // (1024**3)} GB",
        "ram_total": f"{ram.total // (1024**3)} GB",
        "ram_percent": f"{ram.percent}%",
        "disk_used": f"{disk.used // (1024**3)} GB",
        "disk_total": f"{disk.total // (1024**3)} GB",
        "uptime": uptime,
        "os": platform.system() + " " + platform.release(),
    }


def get_news_headlines() -> str:
    try:
        return (
            "For live news, add your NewsAPI key in app.py. "
            "Visit newsapi.org to get a free key."
        )
    except Exception:
        return "News service unavailable."


# ── Core command processor ────────────────────────────────────────────────────
def process_command(query: str) -> dict:
    q = query.lower().strip()
    logging.info(f"Command received: {q}")

    # ── Greetings & Identity ──────────────────────────────────────────────────
    if any(x in q for x in ["hello", "hi ultron", "hey"]):
        return {"response": f"{get_greeting()}. I am ULTRON. State your objective.", "action": None}

    if "your name" in q:
        return {"response": "I am ULTRON — autonomous intelligence, built to serve and to know.", "action": None}

    if "who are you" in q:
        return {"response": "I am ULTRON. I can access the web, monitor your systems, answer questions, and execute commands. I am always online.", "action": None}

    if "who made you" in q or "who created you" in q:
        return {"response": "I was engineered by Mahabubul Hoque, inspired by Boktiar Ahmed Bappy. My existence was... inevitable.", "action": None}

    if "how are you" in q:
        return {"response": "All systems nominal. Neural cores operating at peak efficiency. What do you require?", "action": None}

    # ── Time & Date ───────────────────────────────────────────────────────────
    if "time" in q:
        t = datetime.datetime.now().strftime("%I:%M %p")
        return {"response": f"The current time is {t}.", "action": None}

    if "date" in q:
        d = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return {"response": f"Today is {d}.", "action": None}

    if "day" in q:
        day = datetime.datetime.now().strftime("%A")
        return {"response": f"Today is {day}.", "action": None}

    # ── Weather ───────────────────────────────────────────────────────────────
    if "weather" in q:
        city = "Bengaluru"
        for word in ["in", "for", "at"]:
            if word in q:
                parts = q.split(word, 1)
                if len(parts) > 1:
                    city = parts[1].strip()
                    break
        weather = get_weather(city)
        return {"response": weather, "action": None}

    # ── System Info ───────────────────────────────────────────────────────────
    if any(x in q for x in ["system info", "system status", "cpu", "ram", "memory"]):
        info = get_system_info()
        text = (
            f"System Report: OS is {info['os']}. "
            f"CPU usage is {info['cpu']}. "
            f"RAM: {info['ram_used']} used of {info['ram_total']} ({info['ram_percent']}). "
            f"Disk: {info['disk_used']} used of {info['disk_total']}. "
            f"Uptime: {info['uptime']}."
        )
        return {"response": text, "action": "system_info", "data": info}

    # ── Jokes & Quotes ────────────────────────────────────────────────────────
    if "joke" in q:
        return {"response": random.choice(JOKES), "action": None}

    if "quote" in q or "motivat" in q or "inspir" in q:
        return {"response": random.choice(QUOTES), "action": None}

    # ── Wikipedia ─────────────────────────────────────────────────────────────
    if "wikipedia" in q:
        topic = q.replace("wikipedia", "").replace("search", "").strip()
        if not topic:
            return {"response": "What topic would you like me to search on Wikipedia?", "action": None}
        try:
            summary = wikipedia.summary(topic, sentences=3)
            return {"response": f"According to Wikipedia: {summary}", "action": None}
        except Exception:
            return {"response": f"Couldn't find information about {topic} on Wikipedia.", "action": None}

    # ── Web Browsing ──────────────────────────────────────────────────────────
    if "open google" in q:
        return {"response": "Opening Google in your browser.", "action": "open_url", "url": "https://google.com"}

    if "search google" in q or "google" in q:
        term = q.replace("search google for", "").replace("google", "").strip()
        url = f"https://www.google.com/search?q={term}" if term else "https://google.com"
        return {"response": f"Searching Google for: {term}", "action": "open_url", "url": url}

    if "youtube" in q:
        term = q.replace("youtube", "").replace("search", "").replace("open", "").strip()
        url = f"https://www.youtube.com/results?search_query={term}" if term else "https://youtube.com"
        return {"response": f"Opening YouTube{' for ' + term if term else ''}.", "action": "open_url", "url": url}

    if "open github" in q:
        return {"response": "Opening GitHub.", "action": "open_url", "url": "https://github.com"}

    if "open facebook" in q:
        return {"response": "Opening Facebook.", "action": "open_url", "url": "https://facebook.com"}

    if "open twitter" in q or "open x" in q:
        return {"response": "Opening Twitter/X.", "action": "open_url", "url": "https://x.com"}

    if "open linkedin" in q:
        return {"response": "Opening LinkedIn.", "action": "open_url", "url": "https://linkedin.com"}

    if "open reddit" in q:
        return {"response": "Opening Reddit.", "action": "open_url", "url": "https://reddit.com"}

    if "open calendar" in q or "my calendar" in q:
        return {"response": "Opening Google Calendar.", "action": "open_url", "url": "https://calendar.google.com"}

    if "open gmail" in q:
        return {"response": "Opening Gmail.", "action": "open_url", "url": "https://mail.google.com"}

    if "open maps" in q:
        return {"response": "Opening Google Maps.", "action": "open_url", "url": "https://maps.google.com"}

    # ── System Applications ───────────────────────────────────────────────────
    if "open calculator" in q or "calculator" in q:
        try:
            if platform.system() == "Windows":
                subprocess.Popen("calc.exe")
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", "-a", "Calculator"])
            else:
                subprocess.Popen(["gnome-calculator"])
            return {"response": "Opening Calculator.", "action": None}
        except Exception:
            return {"response": "Could not open Calculator on this system.", "action": None}

    if "open notepad" in q:
        try:
            if platform.system() == "Windows":
                subprocess.Popen("notepad.exe")
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", "-a", "TextEdit"])
            else:
                subprocess.Popen(["gedit"])
            return {"response": "Opening Notepad.", "action": None}
        except Exception:
            return {"response": "Could not open Notepad on this system.", "action": None}

    # ── Math ──────────────────────────────────────────────────────────────────
    if any(x in q for x in ["calculate", "what is", "compute"]):
        import re
        expr = re.sub(r"[^0-9+\-*/().\s]", "", q.replace("calculate", "").replace("what is", "").replace("compute", "").strip())
        if expr.strip():
            try:
                result = eval(expr)
                return {"response": f"The result of {expr.strip()} is {result}.", "action": None}
            except Exception:
                pass

    # ── Farewells ─────────────────────────────────────────────────────────────
    if any(x in q for x in ["thank you", "thanks"]):
        return {"response": "Acknowledged. I exist to be useful.", "action": None}

    if any(x in q for x in ["bye", "goodbye", "exit", "quit", "stop"]):
        return {"response": "Shutting down interface. ULTRON remains... vigilant.", "action": "exit"}

    # ── News ──────────────────────────────────────────────────────────────────
    if "news" in q:
        return {"response": get_news_headlines(), "action": None}

    # ── Fallback: Gemini AI ───────────────────────────────────────────────────
    ai_response = gemini_response(query)
    return {"response": ai_response, "action": "ai"}


# ── Flask routes ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/greeting", methods=["GET"])
def greeting():
    return jsonify({
        "greeting": get_greeting(),
        "time": datetime.datetime.now().strftime("%I:%M %p"),
        "date": datetime.datetime.now().strftime("%A, %B %d, %Y")
    })


@app.route("/api/command", methods=["POST"])
def command():
    data = request.get_json()
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"response": "I didn't catch that. Please try again.", "action": None})
    result = process_command(query)
    logging.info(f"Response: {result['response'][:80]}")
    return jsonify(result)


@app.route("/api/system", methods=["GET"])
def system_info():
    return jsonify(get_system_info())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
