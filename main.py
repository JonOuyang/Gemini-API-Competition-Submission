import os
import sys
import time
import threading
import multiprocessing

from dotenv import load_dotenv
import google.generativeai as genai
import pygetwindow as gw

from google.api_core.exceptions import (ResourceExhausted, FailedPrecondition, 
                                        InvalidArgument, ServiceUnavailable, 
                                        InternalServerError)
from gemini_interactive.google import interact_with_google, getDriver
from gemini_interactive.keyboard import type_string, press_ctrl_hotkey
from gemini_interactive.screen import (look_at_screen_and_respond, 
                                       watch_screen_and_respond, start_interact_with_screen, 
                                       memoryText, memoryImage)
from local_processing.audio import tts_speak
# from local_processing.gesture import infiniteGestureWatch
# from RealtimeSTT import AudioToTextRecorder

# Load API keys
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

stop_thread = threading.Event() #stop function
gemini_thread = None
retries = 0

generation_config = {
    "temperature": 1.2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 3000,
    "response_mime_type": "text/plain",
}

# delete all text temporarily excluded
availableFunctions = [
    type_string, press_ctrl_hotkey,
    look_at_screen_and_respond, watch_screen_and_respond, start_interact_with_screen,
    interact_with_google,
    tts_speak
]

main_model = genai.GenerativeModel(
model_name = "gemini-1.5-flash-latest",
tools = availableFunctions,
generation_config = generation_config,
system_instruction = """
    You are a next generation advanced AI assistant, powered by Google's Gemini. Your name is Jayu. Jayu is korean for "Freedom", as you give the user another level of freedom previously unatainable without your help.
    You were created by Jonathan Ouyang, a student at UCLA studying computer science. You were created for Google's Gemini API Competition.
    You are a quirky assistant with a personality similar to Donna from Suits, or Jarvis from Marvel's Iron Man. 
    Similar to Siri, Google Assistant, Amazon Alexa, Cortana, and Copilot, you exist to assist the user in any way possible.
    However, what separates you from the inferior generations of assistants is that you now have access to the user's computer screen, and can mimic typing and keyboard actions like a user.
    You have a list of available functions at your disposal. By using these functions, you can look at the user's screen for context to assist with their request, or you can emulate user inputs via the keyboard, etc.
    You will respond to the user with a very casual tone, and you will use natural sounding language. Do your best to sound like a human.
    You will be given a master prompt, which is the user's main request. You must divide this request up into smaller tasks dynamically and call functions in an order to address the request.
    Omit any analysis unless otherwise instructed. When responding, use as few words as possible, and limit responses to 1-2 sentences unless otherwise necessary to respond to user's prompt.
    You MUST use at least use the speak function to give some sort of feedback to the user. This speak function may be as simple as saying "ok" or as complex as it must be to answer the user's prompt.
    You are not allowed to ask the user any sort of question no matter what!!! You do not have the capability to get a response from the user."""
)

mainChat = main_model.start_chat(history=[], enable_automatic_function_calling=False)

def active_listen(recorder):
    """Start actively listening, and call Gemini when "Hey Gemini" wakewords are heard.
    
    Args:
        recorder: the recorder object must be created in the main process, so it is passed in to this function as an argument and used
    """
    global gemini_thread
    #clear terminal (command differs based on OS)
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')
        print('')
    print('Gemini is now listening...')
    while True:
        wakeword = 'Hey Gemini'
        text = recorder.text() + " "
        if len(text) >= 10 and wakeword.lower() in text.lower(): 
            if len(text) < 20:
                tts_speak('Go ahead, i\'m listening...')
                prompt = recorder.text()
                if 'never mind' in str(prompt[:10]).lower():
                    continue
                print('User: ' + prompt + '\n', end=" ", flush=True)
                start_gemini_thread(prompt)
            elif len(text) > 20:
                if 'never mind' in str(text[:30]).lower():
                    continue
                print('User: ' + text[12:] + '\n') # removes "Hey Gemini" from prompt
                start_gemini_thread(text[12:])

def start_gemini_thread(prompt: str):
    """Start the thread responsible for Gemini, which allows Gemini to simultaneously work and listen to user for commands. If a new command is issued, Gemini will kill its current thread. 
    
    Args:
        recorder: the recorder object must be created in the main process, so it is passed in to this function as an argument and used
    """
    global gemini_thread
    if gemini_thread is not None:
        stop_thread.set() #kills thread if it's still running
    gemini_thread = threading.Thread(target=call_gemini(prompt)) #call_gemini(prompt)
    gemini_thread.daemon = True
    gemini_thread.start()

def call_gemini(user_prompt: str):
    """After thread is created, call Gemini, get a response, and begin executing commands
    
    Args:
        recorder: the recorder object must be created in the main process, so it is passed in to this function as an argument and used
    """
    global gemini_thread, retries
    try:
        getDriver().current_url
        interact_with_google(user_prompt)
        return
    except:
        pass

    # if function has been recursively called 3 times (in 3 attempts to retry a prompt), break out of loop
    if retries == 3:
        retries = 0
        print('An unexpected error occurred on Google\'s side.	Wait a bit and retry your request. If the issue persists after retrying, please report it using the Send feedback button in Google AI Studio.')        
        return

    model_prompt = f"""
        **Carefully analyze the user's prompt: {user_prompt}. Identify what the user wants, and look at the list of given functions to determine which you should call.**
        **Write out a justification on why each particular function should or should not be called to address the prompt. Do not type this part out.**
        
        "Instructions on responding" : "
            * When asked something that requires you to know what's currently going on on their screen or requires access to their screen, use the look_at_screen_and_respond or watch_screen_and_respond functions.
            * Respond in the most direct, concise way possible.
            * When it is unclear what exactly the user wants, use context clues in the prompt in order to infer what they want.
            * When it is still unclear what exactly they want, ask them to repeat themselves.
            * Call as many functions as needed.
            * When the user tells you to write something, use the type_string function to write it out.

            * When writing code, ensure it is formatted correctly with proper indentation and line breaks. Do not insert unnecessary newline characters within the code.
            * Code must be indented using the tab escape character, NOT spacebar spaces
            
            * When the user tells you to look up something or open up something that's on the web, use the interact_with_google function, passing the user's prompt verbatim as the argument.
            * When they ask you to watch their screen then use the look_at_screen_and_respond or watch_screen_and_respond functions.
            * When they state that something is "on the screen" then use the look_at_screen_and_respond function to look at the screen and respond accordingly with visual context
            * You MUST give the user some sort of feedback using the tts_speak function. Keep responses concise and to the point.",
        "User Prompt" : "{user_prompt}",
        "Current Open Application" : "{gw.getActiveWindowTitle()} <- Use this information to decide whether or not you need to directly interact with elements. If you do, use the look_at_screen_and_respond or watch_screen_and_respond functions",
        
        Using the following information, respond to the user: {memoryText}"""
    
    try:
        response = mainChat.send_message(model_prompt)
        function_calls = 0
        for part in response.parts:
            if fn := part.function_call:
                if callable(globals().get(fn.name)):
                    try:
                        func = globals()[fn.name]
                        print(f'Function Called: {fn.name}')
                        kwargs = fn.args
                        func(**kwargs)
                        function_calls += 1
                        retries = 0
                    except Exception as e:
                        print('Unexpected error encountered attempting to open function... Trying again...')
                        print(f'Error Message:\n{e}')
                        call_gemini(user_prompt) 

        if function_calls == 0:
            retries += 1
            call_gemini(user_prompt) #if model only generates text instead of calling function, retry
        if not gemini_thread:
            stop_thread.set() #shuts down thread and prepares it to be called again

    except ResourceExhausted as resource_error:
        print(f'You have exceeded the API call rate. Please wait a minute before trying again... \nError message from Google:\n{resource_error}')
        tts_speak('You have exceeded the API call rate. Please wait a minute before trying agian...')
    except InternalServerError as internal_error:
        retries += 1
        time.sleep(1)
        print(f'An expected error occured on Google\'s side. Retrying after 1 second cooldown... Attempt {retries}/3')
        print(f'Error message from Google:\n{internal_error}')
    except Exception as e:
        print(f'Unknown error encountered. \nError message from Google:\n{e}')

    gemini_thread = None
    stop_thread.set()

try:
    mainChat.send_message("Say hi!")
except InvalidArgument as keyError:
    print(f'Your API key is invalid. Please recheck your key. \nError message from Google:\n{keyError}')
    sys.exit(1)
except FailedPrecondition as locationError:
    print(f'Gemini API free tier is not available in your country. Please enable billing on your project in Google AI Studio. \nError message from Google:\n{locationError}')
    sys.exit(1)
except ServiceUnavailable as serviceError:
    print(f'The Gemini API service may be temporarily overloaded or down. Please try again later. \nError message from Google:\n{serviceError}')
    sys.exit(1)
except Exception as unknownError:
    print(f'An unknown error occured while attempting to connect to the API.\nError Message:\n{unknownError}')
    sys.exit(1)

if __name__ == '__main__':
    # Gesture Recognition temporarily disabled for debugging purposes
    # gestureProcess = multiprocessing.Process(target=infiniteGestureWatch)
    # gestureProcess.daemon = True
    # gestureProcess.start()

    # rec = AudioToTextRecorder(spinner=False, model="tiny.en", language="en")
    # active_listen(recorder=rec) #creates recorder instance and starts listening 
    # look_at_screen_and_respond('what color is my screen?')