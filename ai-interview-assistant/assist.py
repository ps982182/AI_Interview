import eel
import speech_recognition as sr
from openai import OpenAI
import threading
import json
import os
import time
import re

eel.init('web')

class AudioAssistant:
    def __init__(self):
        self.setup_audio()
        self.is_listening = False
        self.client = None
        self.api_key = None
        self.tts_enabled = False  # TTS disabled for Gemini API
        self.is_speaking = False
        self.audio_playing = False
        self._buffer = ""
        self.load_api_key()

    def setup_audio(self):
        """Robust mic detection with tuned thresholds"""
        self.recognizer = sr.Recognizer()
        try:
            print("Available microphones:")
            for idx, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"  {idx}: {name}")
        except Exception:
            pass

        try:
            self.mic = sr.Microphone()
            print("Using default microphone")
        except OSError:
            mic_list = sr.Microphone.list_microphone_names()
            self.mic = None
            for i, mic_name in enumerate(mic_list):
                try:
                    mic_test = sr.Microphone(device_index=i)
                    self.mic = mic_test
                    print(f"Using microphone {i}: {mic_name}")
                    break
                except OSError:
                    continue
            if self.mic is None:
                raise Exception("No working microphone found")

        with self.mic as source:
            print("Adjusting for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)

        self.recognizer.energy_threshold = max(300, int(self.recognizer.energy_threshold * 1.2))
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.9
        self.recognizer.phrase_threshold = 0.4
        self.recognizer.non_speaking_duration = 0.6
        print(f"Audio setup complete. Energy threshold: {self.recognizer.energy_threshold}")

    def load_api_key(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                key = config.get('api_key')
                if key:
                    self.set_api_key(key)

    def set_api_key(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        with open('config.json', 'w') as f:
            json.dump({'api_key': api_key}, f)

    def delete_api_key(self):
        self.api_key = None
        self.client = None
        if os.path.exists('config.json'):
            os.remove('config.json')

    def has_api_key(self):
        return self.api_key is not None

    def toggle_listening(self):
        if not self.client:
            return False
        self.is_listening = not self.is_listening
        if self.is_listening:
            threading.Thread(target=self.listen_and_process, daemon=True).start()
        return self.is_listening

    def listen_and_process(self):
        print("Listening loop started")
        while self.is_listening:
            if self.is_speaking or self.audio_playing:
                time.sleep(0.1)
                continue
            try:
                print("Awaiting speech...")
                with self.mic as source:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                print("Audio captured. Recognizing...")
                text = self.recognizer.recognize_google(audio, language='en-IN').strip()

                # Buffer short fragments, concatenate until long enough
                if len(text) < 6 or len(text.split()) < 3:
                    self._buffer = (self._buffer + " " + text).strip()
                    print(f"Buffered fragment: '{self._buffer}'")
                    if len(self._buffer) < 12 or len(self._buffer.split()) < 3:
                        continue
                    text = self._buffer
                    self._buffer = ""

                # Show only probable questions or ending with '?'
                if not self.is_question(text) and not text.endswith('?'):
                    print(f"Ignored non-question fragment: '{text}'")
                    continue

                formatted = text.strip()
                if formatted:
                    formatted = formatted[0].upper() + formatted[1:]
                if not formatted.endswith(('?', '.', '!')):
                    formatted += '?' if self.is_question(text) else '.'

                eel.update_ui(f"Q: {formatted}", "")
                self.is_speaking = True
                response = self.get_ai_response(formatted)
                eel.update_ui("", response)
                self.is_speaking = False
                time.sleep(1)
            except sr.WaitTimeoutError:
                print("Timeout: no speech detected")
                continue
            except sr.UnknownValueError:
                print("Could not understand audio")
                continue
            except sr.RequestError as e:
                msg = f"Speech service error: {e}"
                print(msg)
                eel.update_ui("", json.dumps({"text": msg, "audio": None}))
                time.sleep(2)
            except Exception as e:
                msg = f"Error: {str(e)}"
                print(msg)
                eel.update_ui("", json.dumps({"text": msg, "audio": None}))
                time.sleep(1)

    def is_question(self, text):
        t = text.lower().strip()
        starters = [
            "what","why","how","when","where","who","which",
            "can","could","would","should","is","are","do","does",
            "am","was","were","have","has","had","will","shall"
        ]
        if any(t.startswith(s) for s in starters):
            return True
        if t.endswith('?'):
            return True
        if re.match(r'^(are|can|could|do|does|have|has|will|shall|should|would|am|is)\s', t):
            return True
        phrases = [
            "tell me about","i'd like to know","can you explain",
            "i was wondering","do you know","what about","how about",
            "help me","show me","explain","describe"
        ]
        return any(p in t for p in phrases)

    def get_ai_response(self, question):
        try:
            print(f"Sending to Gemini: {question}")
            resp = self.client.chat.completions.create(
                model="gemini-1.5-flash",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for interview preparation. Provide clear, concise, and professional answers."},
                    {"role": "user", "content": question}
                ]
            )
            text = resp.choices[0].message.content.strip()
            return json.dumps({"text": text, "audio": None})
        except Exception as e:
            err = f"Error getting AI response: {str(e)}"
            print(err)
            return json.dumps({"text": err, "audio": None})

@eel.expose
def test_microphone():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            print("Mic test: speak now...")
            audio = r.listen(source, timeout=5, phrase_time_limit=3)
            text = r.recognize_google(audio, language='en-IN')
            return f"SUCCESS: Heard '{text}'"
    except Exception as e:
        return f"ERROR: {str(e)}"

assistant = AudioAssistant()

@eel.expose
def toggle_listening():
    return assistant.toggle_listening()

@eel.expose
def save_api_key(api_key):
    try:
        assistant.set_api_key(api_key)
        return True
    except Exception as e:
        print(f"Error saving API key: {str(e)}")
        return False

@eel.expose
def delete_api_key():
    try:
        assistant.delete_api_key()
        return True
    except Exception as e:
        print(f"Error deleting API key: {str(e)}")
        return False

@eel.expose
def has_api_key():
    return assistant.has_api_key()

@eel.expose
def toggle_tts():
    assistant.tts_enabled = False
    return assistant.tts_enabled

@eel.expose
def speaking_ended():
    assistant.is_speaking = False

@eel.expose
def audio_playback_started():
    assistant.audio_playing = True

@eel.expose
def audio_playback_ended():
    assistant.audio_playing = False
    assistant.is_speaking = False

eel.start('index.html', size=(1000, 900))
