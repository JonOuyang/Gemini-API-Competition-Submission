import os
import requests
import vlc
import logging
import threading
import time

logging.basicConfig(level=logging.ERROR)
from dotenv import load_dotenv

# Load API keys
load_dotenv()
CHUNK_SIZE = 1024
url = os.getenv("ELEVENLABS_URL")

headers = {
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": os.getenv("ELEVENLABS_API_KEY") # 11labs api key
}

def play_audio():
  audioPlayer = vlc.MediaPlayer("JayuAudio.mp3")
  audioPlayer.play()
  time.sleep(audioPlayer.get_length()/1000+1)

def tts_speak(text: str):
  """Verbally tell something to the user
        
    Args:
        text: the text to be spoken to the user, passed as a string.
    """
  # Text preprocessing to get rid of extra escape characters
  text = text.replace("\'", "'")
  text = text.replace("\\'", "\'")
  text = text.replace('\\\\', '\\')
  text = text.replace('\\n', '\n')
  text = text.replace('\\r', '\r')
  text = text.replace('\\t', '\t')
  text = text.replace('\\b', '\b')
  text = text.replace('\\f', '\f') 
  print(f'Gemini: {text}')

  global audioPlayer
  data = {
    "text": text,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
      "stability": 0.5,
      "similarity_boost": 0.5
    }
  }
  response = requests.post(url, json=data, headers=headers, stream=True)
  if response.status_code == 200:
    with open('JayuAudio.mp3', 'wb') as f:
      for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
          if chunk:
              f.write(chunk)
  else:
    print('call failed')

  audio_thread = threading.Thread(target=play_audio)
  audio_thread.start()
  audio_thread.join()

def stop_speaking():
  """Function to stop the running auditory feedback. This function should be called when you want to stop talking and listen to the user
        
    Args:
        None
  """
  audioPlayer.stop()
