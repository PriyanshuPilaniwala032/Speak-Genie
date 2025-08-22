import speech_recognition as sr
import google.generativeai as genai # New import for Gemini
from gtts import gTTS
import os
import playsound
from langdetect import detect, LangDetectException
import re
import dotenv

dotenv.load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r'', text)

# Function to listen to the user's voice and convert it to text
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

# Function to convert text to speech with language detection
def speak(text):
    text_to_speak = remove_emojis(text)
    if not text_to_speak.strip():
        return

    try:
        lang_code = detect(text_to_speak)
    except LangDetectException:
        lang_code = 'en'

    try:
        tts = gTTS(text=text_to_speak, lang=lang_code)
        filename = "response.mp3"
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"Error during text-to-speech: {e}")


def get_ai_response(chat_session, prompt):
    try:
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        print(f"Error getting response from Gemini: {e}")
        return "Sorry, I'm having trouble responding right now."

# Function to generate a report on the user's performance 
def generate_report(conversation_history):
    report_model = genai.GenerativeModel('gemini-1.5-flash')
    report_chat = report_model.start_chat(history=conversation_history)
    
    report_prompt = "Based on our conversation, please provide a simple, two-sentence report on my English speaking performance. Mention one thing I did well and one thing to improve."
    
    try:
        report = report_chat.send_message(report_prompt).text
        print("\n---------- Instant Report ----------")
        print(report)
        print("------------------------------------")
    except Exception as e:
        print(f"Could not generate report: {e}")

# Personal Chatbot mode
def personal_chatbot():
    print("Welcome to the Personal Chatbot!")
    print("You can start speaking now. Say 'quit' to exit.")

    system_prompt = (
        "You are a friendly and encouraging English tutor for children. Keep your responses short and engaging. "
        "IMPORTANT: If the user speaks in a language other than English, you MUST reply in that same language."
    )
    
    chat = gemini_model.start_chat(history=[{'role': 'user', 'parts': [system_prompt]}, {'role': 'model', 'parts': ["Of course! I'm ready to help."]}])
    
    while True:
        user_input = listen()
        if user_input:
            if 'quit' in user_input.lower():
                break
            ai_response = get_ai_response(chat, user_input)
            print(f"AI Tutor: {ai_response}")
            speak(ai_response)
            generate_report(chat.history)

# Function to handle roleplay scenarios
def roleplay():
    roleplay_scenarios = {
        "1": "At School",
        "2": "At the Store",
        "3": "At Home"
    }
    print("Welcome to Roleplay Mode!")
    print("Choose a scenario:")
    for key, value in roleplay_scenarios.items():
        print(f"{key}. {value}")
    choice = input("Enter the number of the scenario: ")
    if choice in roleplay_scenarios:
        scenario = roleplay_scenarios[choice]
        print(f"You have chosen: {scenario}")
        print("You can start speaking now. Say 'quit' to exit.")
        
        system_prompt = (
            f"Let's roleplay. The scenario is '{scenario}'. You are a friendly character in this scenario, and I am a child learning English. "
            "IMPORTANT: If I speak in a language other than English, you MUST reply in that same language. "
            "Now, please start the conversation."
        )
        chat = gemini_model.start_chat(history=[{'role': 'user', 'parts': [system_prompt]}, {'role': 'model', 'parts': ["Sounds fun! Let's begin."]}])

        initial_response = chat.history[-1].parts[0].text
        print(f"AI Tutor: {initial_response}")
        speak(initial_response)

        while True:
            user_input = listen()
            if user_input:
                if 'quit' in user_input.lower():
                    break
                ai_response = get_ai_response(chat, user_input)
                print(f"AI Tutor: {ai_response}")
                speak(ai_response)
                generate_report(chat.history)
    else:
        print("Invalid choice. Please try again.")

def main():
    while True:
        print("\nWelcome to the Real-Time AI Voice English Tutor!")
        print("1. Personal Chatbot")
        print("2. Roleplay Mode")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            personal_chatbot()
        elif choice == '2':
            roleplay()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
