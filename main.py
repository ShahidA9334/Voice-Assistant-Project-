# from pathlib import Path
# from openai import OpenAI
# import pygame
# import time
# import os


# def text_to_speech(text):
    
#     client = OpenAI()

#     speech_file_path = Path(_file_).parent / "speech2.mp3"
#     os.remove(speech_file_path)

#     with client.audio.speech.with_streaming_response.create(
#         model="tts-1",
#         voice="nova",
#         input=text,
#     ) as response:
#         response.stream_to_file(speech_file_path)

#     pygame.mixer.init()
#     pygame.mixer.music.load(speech_file_path)
#     pygame.mixer.music.play()

#     # Keep the program running long enough for the audio to play
#     while pygame.mixer.music.get_busy():
#         time.sleep(1)

#     pygame.mixer.quit()


import pyttsx3

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Open Python in Command Prompt
   
# import os

# file_path = os.path.join(os.path.dirname(__file__), "credentials.json")

# with open(file_path, "r") as file:
#     data = file.read()


# from pathlib import Path
# import pygame
# import time
# import os

# def text_to_speech(text):
#     try:
#         # Define the output file path
#         speech_file_path = Path(__file__).parent / "speech2.mp3"

#         # Remove existing file if it exists
#         if speech_file_path.exists():
#             os.remove(speech_file_path)

#         # Replace this with the actual TTS API or library call
#         # Example: Generate an MP3 file with the text content
#         with open(speech_file_path, "wb") as f:
#             from gtts import gTTS
#             tts = gTTS(text)
#             tts.write_to_fp(f)

#         # Play the generated MP3 file
#         pygame.mixer.init()
#         pygame.mixer.music.load(str(speech_file_path))
#         pygame.mixer.music.play()

#         # Wait until the audio finishes playing
#         while pygame.mixer.music.get_busy():
#             time.sleep(1)

#         pygame.mixer.quit()

#     except Exception as e:
#         print(f"Error in text_to_speech: {e}")

    

# from gtts import gTTS
# from pathlib import Path
# import pygame
# import time
# import os

# def text_to_speech(text):
#     try:
#         # Define the output file path
#         speech_file_path = Path(__file__).parent / "speech2.mp3"

#         # Remove existing file if it exists
#         if speech_file_path.exists():
#             os.remove(speech_file_path)

#         # Generate speech with gTTS
#         tts = gTTS(text)
#         tts.save(speech_file_path)

#         # Play the generated MP3 file
#         pygame.mixer.init()
#         pygame.mixer.music.load(str(speech_file_path))
#         pygame.mixer.music.play()

#         # Wait until the audio finishes playing
#         while pygame.mixer.music.get_busy():
#             time.sleep(1)

#         pygame.mixer.quit()

#     except Exception as e:
#         print(f"Error in text_to_speech: {e}")