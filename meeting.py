import undetected_chromedriver as uc
from time import sleep
from selenium.webdriver.common.by import By
import speech_recognition as sr
import pyttsx3
import random
import asyncio
from agent.ok import getAnswer

async def run_meeting(meetingInfo):
    """Run the meeting process asynchronously."""
    meetLink = meetingInfo["meetingLink"]
    teamName = meetingInfo["teamName"]

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
    await asyncio.sleep(3)

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
                print(f"{description} button not found. Retrying...")
                sleep(2)

    # Turn off microphone and camera
    # toggle_button("//div[@aria-label='Turn off microphone']", "Microphone")
    toggle_button("//div[@aria-label='Turn off camera']", "Camera")

    recognizer = sr.Recognizer()
    tts_engine = pyttsx3.init()
    
    def speak(text):
        """Speak the text using pyttsx3."""
        tts_engine.say(text)
        tts_engine.runAndWait()

    def speak_while_fetching():
        """Speak thinking phrases continuously to cover lag time."""
        thinking_phrases = ["Hmmmm.", "Let me think", "Just a moment"]
        speak(random.choice(thinking_phrases))
        return

    # def get_AI_response(question):
    #     """Simulate AI response generation."""
    #     return f"Thank you for the question: {question}"

    # Enter the name "Agent"
    while True:
        try:
            enterName = driver.find_element(By.XPATH, "//input[@aria-label='Your name']")
            enterName.clear()
            enterName.send_keys("Agent")
            break
        except Exception as e:
            print('Your name input not found. Retrying...')
            await asyncio.sleep(2)

    # Click "Ask to join" or "Join now" button
    while True:
        try:
            try:
                askToJoinButton = driver.find_element(By.XPATH, "//span[contains(text(), 'Ask to join')]")
            except:
                askToJoinButton = driver.find_element(By.XPATH, "//span[contains(text(), 'Join now')]")
            askToJoinButton.click()
            print("Meeting Joined")
            break
        except Exception as e:
            print("'Ask to join' button not found. Retrying...")
            await asyncio.sleep(2)

    # Wait for a moment to ensure the meeting interface is fully loaded
    await asyncio.sleep(5)

    # Ensure no one is talking before greeting
    recognizer = sr.Recognizer()
    mic_device_index = None
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        if "VB-Audio" in name:
            mic_device_index = index
            break

    if mic_device_index is not None:
        with sr.Microphone(device_index=mic_device_index) as source:
            try:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Checking if the room is silent...")
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                # If audio is detected, assume someone is talking
                detected_text = recognizer.recognize_google(audio)
                print(f"Detected speech: {detected_text}. Delaying greeting...")
                await asyncio.sleep(5)  # Wait and retry
            except sr.WaitTimeoutError:
                # No speech detected, safe to greet
                print("Room is silent. Greeting the team.")
                speak(f"Hi {teamName} Team!")
            except sr.UnknownValueError:
                print("Could not understand audio, assuming silence.")
                speak(f"Hi {teamName} Team!")
            except sr.RequestError as e:
                print(f"Error checking room silence: {e}. Skipping greeting.")

    # ------------------ Voice Trigger Agent Code ------------------ #

    mic_device_index = None
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        if "VB-Audio" in name:
            mic_device_index = index
            print(f"Using VB-Audio device for input: {name} (Index {index})")
            break

    if mic_device_index is None:
        print("VB-Audio device not found. Using default microphone.")

    print("Agent is listening for the trigger phrase 'Hey Agent' or meeting end phrase 'Thank you for attending'...")

    try:
        while True:
            with sr.Microphone(device_index=mic_device_index) as source:
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=5)
                    text = recognizer.recognize_google(audio).lower()
                    print("Recognized:", text)
                    
                    # Trigger only when "hey agent" or "a agent" is explicitly mentioned
                    if "hey agent" in text or "a agent" in text:
                        speak("How may I help you?")
                        print("Listening for context...")
                        try:
                            context_audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                            context_text = recognizer.recognize_google(context_audio)
                            print("Context recognized:", context_text)

                            speak_while_fetching()

                            try:
                                answer = getAnswer(context_text)
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
                    
                    elif "thank you for attending" in text or "thanks for attending" in text:
                        print("End phrase detected. Ending the meeting...")
                        while True:
                            try:
                                # Updated XPath to use aria-label for the "Leave call" button
                                leave_button = driver.find_element(By.XPATH, "//button[@aria-label='Leave call']")
                                leave_button.click()
                                print("Meeting ended successfully.")
                                break  # Exit the loop after successfully clicking the button
                            except Exception as e:
                                print(f"Error while trying to leave the meeting: {e}")
                                await asyncio.sleep(2)
                        return

                except sr.WaitTimeoutError:
                    print("Listening timed out. Trying again...")
                    continue
                except sr.UnknownValueError:
                    print("Could not understand audio.")
                except sr.RequestError as e:
                    print(f"Could not request results;")
    except KeyboardInterrupt:
        print("Meeting ended.")
    finally:
        driver.quit()