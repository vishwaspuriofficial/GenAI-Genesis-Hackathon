import undetected_chromedriver as uc
from time import sleep
from selenium.webdriver.common.by import By
import speech_recognition as sr
import pyttsx3
import random

# ------------------ Google Meet Joining Code ------------------ #

meetLink = 'Enter Meet Link'

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

prefs = {
    "profile.default_content_setting_values.media_stream_mic": 1,
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.geolocation": 1,
}
options.add_experimental_option("prefs", prefs)
driver = uc.Chrome(options=options)

driver.get(meetLink)
sleep(3)

def toggle_button(xpath, description):
    """Toggle a button (mic or video) based on its XPath."""
    while True:
        try:
            button = driver.find_element(By.XPATH, xpath)
            if button.get_attribute("data-is-muted") != "true":
                button.click()
                print(f"{description} turned off.")
            else:
                print(f"{description} is already off.")
            break 
        except Exception as e:
            print(f"{description} button not found. Retrying... ({e})")
            sleep(2)

# Turn off microphone and camera
# toggle_button("//div[@aria-label='Turn off microphone']", "Microphone")
toggle_button("//div[@aria-label='Turn off camera']", "Camera")

# Enter the name "Agent"
while True:
    try:
        enterName = driver.find_element(By.XPATH, "//input[@aria-label='Your name']")
        enterName.clear()
        enterName.send_keys("Agent")
        break
    except Exception as e:
        print('Your name input not found. Retrying...', e)
        sleep(2)

# Click "Ask to join" or "Join now" button
while True:
    try:
        try:
            askToJoinButton = driver.find_element(By.XPATH, "//span[contains(text(), 'Ask to join')]")
        except:
            askToJoinButton = driver.find_element(By.XPATH, "//span[contains(text(), 'Join now')]")
        askToJoinButton.click()
        print("Meeting Joined")
        break  # Exit loop if successful
    except Exception as e:
        print("'Ask to join' button not found. Retrying...", e)
        sleep(2)

# ------------------ Voice Trigger Agent Code ------------------ #

# List available microphone devices for reference
# print("Available microphone devices:")
# for index, name in enumerate(sr.Microphone.list_microphone_names()):
#     print(f"{index}: {name}")

# Set the device index to the VB-Audio device.
# Adjust the string below to match your device name if needed.
mic_device_index = None
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    if "VB-Audio" in name:
        mic_device_index = index
        print(f"Using VB-Audio device for input: {name} (Index {index})")
        break

if mic_device_index is None:
    print("VB-Audio device not found. Using default microphone.")
    
# Initialize the recognizer and TTS engine.
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

def speak(text):
    """Speak the text using pyttsx3.
       Ensure your default playback device is set to 'Cable Input (VB-Audio Virtual Cable)' in Windows settings."""
    tts_engine.say(text)
    tts_engine.runAndWait()

def speak_while_fetching():
    """Speak thinking phrases continuously to cover lag time."""
    thinking_phrases = ["Hmmmm.", "Let me think", "Just a moment"]
    speak(random.choice(thinking_phrases))
    return

def get_AI_response(question):
    """Simulate AI response generation."""
    return f"Thank you for the question: {question}"

print("Agent is listening for the trigger phrase 'Hey Agent'...")

# Continuously listen for speech.
while True:
    with sr.Microphone(device_index=mic_device_index) as source:
        try:
            # Adjust for ambient noise from the meeting audio.
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # print("Listening from VB-Audio input...")
            # Listen with a timeout to prevent hanging.
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print("Recognized:", text)
            # Trigger when the phrase "hey agent" is mentioned.
            if "hey agent" or "a agent" in text.lower():
                speak("How may I help you?")
                print("Listening for context...")
                # Listen for additional context for 3 seconds of silence.
                try:
                    context_audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    context_text = recognizer.recognize_google(context_audio)
                    print("Context recognized:", context_text)
                    
                    speak_while_fetching()

                    # Call the AI response function
                    try:
                        # Fetch the answer synchronously
                        answer = get_AI_response(context_text)
                        print("Answer received:", answer)
                        speak(answer)
                        continue
                    except Exception as e:
                        print(f"Error processing the request: {e}")
                        speak("I couldn't process your request due to an error.")
                except sr.WaitTimeoutError:
                    print("No question asked!")
                except sr.UnknownValueError:
                    print("Could not understand additional context.")
                except sr.RequestError as e:
                    print(f"Could not request results for context; {e}")
        except sr.WaitTimeoutError:
            print("Listening timed out. Trying again...")
            continue
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")