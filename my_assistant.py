import requests
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import time
import smtplib
import spacy
import pywhatkit  

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize the speech engine
engine = pyttsx3.init()

# Function to convert text to speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to process and analyze commands with spaCy
def process_with_spacy(text):
    doc = nlp(text)
    result = []
    for token in doc:
        result.append(f"{token.text} (Lemma: {token.lemma_}, POS: {token.pos_}, Dependency: {token.dep_})")
    return "\n".join(result)

# Function to get weather details using OpenWeatherMap API
def get_weather(city):
    api_key = "a9cbf53e04f5e313ea2addee96c97024"  # Replace with your OpenWeatherMap API key
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(base_url)
        weather_data = response.json()

        if weather_data["cod"] == "404":
            speak("City not found, please try again.")
            return "City not found."
        else:
            main = weather_data["main"]
            temperature = main["temp"]
            weather_desc = weather_data["weather"][0]["description"]
            result = f"The current temperature in {city} is {temperature} degrees Celsius with {weather_desc}."
            speak(result)
            return result
    except Exception as e:
        print(f"Error in get_weather: {e}")
        speak("Sorry, I couldn't retrieve the weather details right now.")
        return str(e)

# Function to send an email
def send_email(to_email, subject, body):
    sender_email = "your_email@example.com"  # Replace with your email
    password = "your_password"  # Replace with your password
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender_email, to_email, message)
        speak("Email has been sent.")
    except Exception as e:
        print(f"Error in send_email: {e}")
        speak("Failed to send the email. Please check your login details and internet connection.")

# Function to set a reminder
def set_reminder(reminder, seconds):
    speak(f"Reminder set: {reminder}")
    time.sleep(seconds)
    speak(f"Reminder: {reminder}")

# Function to handle various commands
def handle_command(command):
    if 'wikipedia' in command:
        speak("Searching Wikipedia...")
        query = command.replace("wikipedia", "").strip()
        result = wikipedia.summary(query, sentences=2)
        return f"According to Wikipedia: {result}"
    elif 'play' in command:
        song = command.replace('play', '').strip()
        pywhatkit.playonyt(song)
        return f"Playing {song} on YouTube"
    elif 'analyze' in command:
        return process_with_spacy(command)
    elif 'time' in command:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        return f"The current time is {current_time}"
    elif 'weather' in command:
        speak("Which city's weather would you like to know?")
        city = listen()  # Listen for the city name
        if city:
            return get_weather(city)
    elif 'reminder' in command:
        speak("What should I remind you about?")
        reminder = listen()
        speak("In how many seconds?")
        seconds = int(listen())  # Ensure this is a valid integer
        set_reminder(reminder, seconds)
        return f"Reminder set for {seconds} seconds."
    elif 'email' in command:
        speak("Who should I send the email to?")
        to_email = listen()  # This will be an email address in a real-world scenario
        speak("What should be the subject?")
        subject = listen()
        speak("What should be the body of the email?")
        body = listen()
        send_email(to_email, subject, body)
        return "Email sent!"
    elif 'stop' in command or 'exit' in command:
        speak("Goodbye!")
        exit()
    else:
        return "Sorry, I did not understand that command."

# Function to listen to user voice and convert to text
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language='en-in')
            print(f"You said: {query}")
        except Exception as e:
            print("Could not understand your voice, please repeat.")
            return None
    return query.lower()

# Function to greet the user
def greet_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    speak("I am your assistant. How can I help you today?")

# Main function to run the assistant
if __name__ == "__main__":
    greet_user()
    while True:
        command = listen()
        if command:
            response = handle_command(command)
            if response:
                speak(response)
