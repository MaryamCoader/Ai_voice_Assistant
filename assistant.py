import tkinter as tk
from tkinter import scrolledtext, ttk
from googletrans import Translator
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import webbrowser
import requests
import threading
import os
from dotenv import load_dotenv

load_dotenv()

translator = Translator()
recognizer = sr.Recognizer()
is_listening = False

# --- Safe Output Update ---
def update_output(text):
    def append_text():
        output_area.configure(state='normal')
        output_area.insert(tk.END, text + "\n")
        output_area.configure(state='disabled')
        output_area.see(tk.END)
    window.after(0, append_text)

# --- Speak ---
def speak(text):
    update_output(f"Assistant: {text}")
    try:
        engine = pyttsx3.init('sapi5')
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        update_output(f"Speak Error: {e}")

# --- Listen ---
def listen_command():
    global is_listening
    is_listening = True
    while is_listening:
        try:
            with sr.Microphone() as source:
                update_output("🎧 Listening...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                update_output(f"You said: {command}")
                handle_command(command)
        except sr.UnknownValueError:
            update_output("❌ Could not understand.")
        except sr.WaitTimeoutError:
            update_output("⌛ Timeout.")
        except Exception as e:
            update_output(f"⚠️ Error: {e}")

# --- Commands ---
def handle_command(command):
    if "time" in command:
        speak(datetime.datetime.now().strftime("The time is %I:%M %p"))

    elif "joke" in command:
        speak("Why don't scientists trust atoms? Because they make up everything!")

    elif "search" in command:
        speak("What should I search?")
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            query = recognizer.recognize_google(audio)
            webbrowser.open(f"https://www.google.com/search?q={query}")
            speak(f"Searching for {query}")

    elif "youtube" in command:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube")

    elif "google" in command:
        webbrowser.open("https://www.google.com")
        speak("Opening Google")

    elif "play" in command:
        speak("What song should I play?")
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            song = recognizer.recognize_google(audio)
            pywhatkit.playonyt(song)
            speak(f"Playing {song} on YouTube")

    elif "news" in command:
      try:
          speak("Fetching the latest news.")
          api_key = os.getenv("NEWS_API_KEY")  # <-- env se key lena
          if not api_key:
            speak("News API key not found. Please check your .env file.")
            return
        
          url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
          articles = requests.get(url).json().get("articles", [])
        
          if articles:
            for article in articles[:5]:
                speak(article.get("title"))
          else:
            speak("No news found.")
      except Exception as e:
        update_output(f"News Error: {e}")


    elif "reminder" in command:
        speak("What should I remind you about?")
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            reminder = recognizer.recognize_google(audio)
            speak(f"Meeting at 3 PM: {reminder}")

    elif "calculator" in command:
        speak("What calculation?")
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            calc = recognizer.recognize_google(audio)
            try:
                result = eval(calc)
                speak(f"The result is {result}")
            except Exception as e:
                speak("Invalid calculation.")
                update_output(f"Calculator Error: {e}")

    elif "open" in command:
        speak("Which application?")
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            app = recognizer.recognize_google(audio)
            if "notepad" in app.lower():
                os.system("start notepad.exe")
                speak("Opening Notepad")
            elif "calculator" in app.lower():
                os.system("start calc.exe")
                speak("Opening Calculator")
            else:
                speak(f"Sorry, I can't open {app}.")

    elif "translate" in command:
        try:
            speak("What should I translate?")
            with sr.Microphone() as source:
                text = recognizer.listen(source)
                text_to_translate = recognizer.recognize_google(text)

            speak("Which language?")
            with sr.Microphone() as source:
                lang_audio = recognizer.listen(source)
                target_lang = recognizer.recognize_google(lang_audio).lower()

            lang_dict = {
                "french": "fr", "german": "de", "spanish": "es",
                "urdu": "ur", "hindi": "hi", "arabic": "ar",
                "chinese": "zh-cn", "english": "en"
            }

            if target_lang in lang_dict:
                translated = translator.translate(text_to_translate, dest=lang_dict[target_lang])
                speak(f"The translation in {target_lang} is: {translated.text}")
            else:
                speak("Sorry, I don't support that language.")
        except Exception as e:
            update_output(f"Translate Error: {e}")

    elif "alarm" in command:
        speak("What time should I set the alarm for?")
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            alarm_time = recognizer.recognize_google(audio)
            speak(f"Alarm set for 6:30 AM {alarm_time}. (Just a placeholder)")

    elif "exit" in command or "quit" in command:
        speak("Goodbye!")
        stop_listening()
        window.destroy()

    elif "weather" in command:
        try:
            speak("Which city?")
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)
            _ = recognizer.recognize_google(audio)
            city = "Lahore"
            update_output(f"📍 Detected city: {city}")
            get_weather(city)
        except sr.UnknownValueError:
            speak("Sorry, I could not understand the city name.")
        except Exception as e:
            update_output(f"City Listening Error: {e}")

    else:
        speak("Sorry, I can't do that yet.")

# --- Weather ---
def get_weather(city):
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            speak("API key not found. Please check your .env file.")
            return
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") == 200:
            weather = response["weather"][0]["description"]
            temperature = response["main"]["temp"]
            speak(f"The weather in {city} is {weather} with a temperature of {temperature}°C.")
        else:
            speak(f"Sorry, I couldn't find weather for {city}.")
    except Exception as e:
        update_output(f"Weather Error: {e}")

# --- Thread Controls ---
def start_listening():
    speak("Hello! I am your AI Assistant. How can I help you today?")
    threading.Thread(target=listen_command, daemon=True).start()

def stop_listening():
    global is_listening
    is_listening = False
    update_output("🔇 Assistant stopped listening.")

# --- Modern Fullscreen UI ---
window = tk.Tk()
window.title("🎤 AI Voice Assistant")
window.state('zoomed')  # Fullscreen window
window.configure(bg="#0A0A0A")

# Transparent chat frame
chat_frame = tk.Frame(window, bg="#1E1E1E", bd=2, relief="flat")
chat_frame.place(relx=0.5, rely=0.45, anchor="center", width=950, height=500)


title = tk.Label(chat_frame, text="🤖 AI Voice Assistant",
                 font=("Segoe UI", 20, "bold"),
                 bg="#1E1E1E", fg="#03DAC6")
title.pack(pady=10)

output_area = scrolledtext.ScrolledText(chat_frame, width=70, height=15,
                                        font=("Consolas", 10),
                                        bg="#121212", fg="#FFFFFF",
                                        insertbackground="white", borderwidth=0)
output_area.pack(pady=10)
output_area.configure(state='disabled')

# Button frame just below chat
button_frame = tk.Frame(window, bg="#0A0A0A")
button_frame.place(relx=0.5, rely=0.8, anchor="center")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",
                font=("Segoe UI", 11, "bold"),
                padding=10,
                relief="flat",
                background="#03DAC6",
                foreground="black")
style.map("TButton",
          background=[("active", "#00BFA5")])

start_btn = ttk.Button(button_frame, text="▶ Start Listening", command=start_listening)
start_btn.grid(row=0, column=0, padx=15)

stop_btn = ttk.Button(button_frame, text="⏹ Stop Listening", command=stop_listening)
stop_btn.grid(row=0, column=1, padx=15)

exit_btn = ttk.Button(button_frame, text="❌ Exit", command=window.destroy)
exit_btn.grid(row=0, column=2, padx=15)

window.mainloop()

