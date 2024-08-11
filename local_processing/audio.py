import logging
import os
import requests
import time
import vlc

from dotenv import load_dotenv
from RealtimeSTT import AudioToTextRecorder  

# Load API keys
load_dotenv()
CHUNK_SIZE = 1024
url = os.getenv("ELEVENLABS_URL")

headers = {
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": os.getenv("ELEVENLABS_API_KEY") # 11labs api key
}

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
  """
  # re-indent this later to be in the tts_speak function
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
  print('phase 1')
  if response.status_code == 200:
    with open('test.mp3', 'wb') as f:
      for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
          if chunk:
              f.write(chunk)
  else:
    print('call failed')
  print('Attempting to play sound...')

  # WARNING: THIS REQUIRES SOME FUNCTION IN THE CODE TO BE CONSTANTLY RUNNING IN THE BACKGROUND, THIS EXECUTION IS INSTANT
  audioPlayer = vlc.MediaPlayer("test.mp3")
  audioPlayer.play()
  #time.sleep(10) #temporary to play full audio. this can be removed later with continuous runtime
  
  """

def stop_speaking():
  """Function to stop the running auditory feedback. This function should be called when you want to stop talking and listen to the user
        
    Args:
        None
  """
  audioPlayer.stop()
