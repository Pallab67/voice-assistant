from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import openai
import wikipedia
from googletrans import Translator
import paho.mqtt.client as mqtt
import webbrowser

app = Flask(__name__)

# OpenAI API Key (Replace with your own)
openai.api_key = "your-openai-api-key"

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

def speak(text, language='en'):
    """Convert text to speech"""
    engine = pyttsx3.init()  # Initialize a new engine each time
    engine.setProperty('voice', 'english')
    engine.say(text)
    engine.runAndWait()
    engine.stop()  # Ensure the engine stops properly


def recognize_speech():
    """Recognize speech input from the microphone"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio).lower()
        print("You said:", command)
        return command
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.RequestError:
        return "Check your internet connection."

def get_info(query):
    """Fetch information using Wikipedia"""
    try:
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find information on that."

def ask_openai(query):
    """Fetch answers from OpenAI GPT"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful AI assistant."},
                  {"role": "user", "content": query}]
    )
    return response["choices"][0]["message"]["content"]

def translate_text(text, dest_lang):
    """Translate text to another language"""
    translator = Translator()
    translated = translator.translate(text, dest=dest_lang)
    return translated.text

def control_device(command):
    """Connect to an IoT device and control it"""
    mqtt_client = mqtt.Client()
    mqtt_client.connect("your-mqtt-broker-ip", 1883, 60)
    if "turn on light" in command:
        mqtt_client.publish("home/light", "ON")
        return "Turning on the light"
    elif "turn off light" in command:
        mqtt_client.publish("home/light", "OFF")
        return "Turning off the light"
    return "I don't know this command for devices."

def search_google(query):
    """Perform a Google search for products or images"""
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Showing results for {query} on Google."

def process_command(command):
    """Process user commands"""
    if "hello" in command:
        return "Hello! How can I assist you today?"
    elif "who is" in command or "tell me about" in command:
        topic = command.replace("who is", "").replace("tell me about", "").strip()
        return get_info(topic)
    elif "what is" in command:
        return ask_openai(command)
    elif "translate" in command:
        words = command.replace("translate", "").strip().split(" to ")
        if len(words) == 2:
            return translate_text(words[0], words[1])
    elif "turn on" in command or "turn off" in command:
        return control_device(command)
    elif "find" in command or "search for" in command or "show me" in command:
        product = command.replace("find", "").replace("search for", "").replace("show me", "").strip()
        return search_google(product)
    elif "exit" in command or "stop" in command:
        return "Goodbye!"
    else:
        return "I didn't understand that."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    user_input = data.get("text")

    if user_input:
        response_text = process_command(user_input)
        speak(response_text)  # Make the assistant talk
        return jsonify(response_text)
    return jsonify("Sorry, I couldn't understand.")

if __name__ == "__main__":
    app.run(debug=True)