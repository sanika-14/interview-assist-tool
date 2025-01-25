try:
    import pyaudio
    import speech_recognition as sr
    import time
except ImportError as e:
    print(f"Import error: {e}")

def transcribe_audio(duration=30*60):
    """Captures and transcribes live audio for a specified duration (default is 30 minutes)."""
    if pyaudio is None:
        print("PyAudio is not installed. Please install it to use this feature.")
        return None

    recognizer = sr.Recognizer()
    end_time = time.time() + duration
    transcriptions = []

    with sr.Microphone() as source:
        print("Listening for live audio... (Press Ctrl+C to stop)")
        while time.time() < end_time:
            try:
                audio = recognizer.listen(source, timeout=10)
                transcription = recognizer.recognize_google(audio)
                print("Transcription:", transcription)
                transcriptions.append(transcription)
            except sr.UnknownValueError:
                print("Sorry, I couldn't understand the audio.")
            except sr.RequestError as e:
                print(f"API error: {e}")
            except KeyboardInterrupt:
                print("Stopping transcription.")
                break

    return " ".join(transcriptions)

if __name__ == "__main__":
    print("Starting Live Audio Transcription")