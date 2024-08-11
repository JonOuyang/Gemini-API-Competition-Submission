import os
import time

from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted, InternalServerError
import google.generativeai as genai
import pyautogui
from PIL import Image, ImageGrab, PngImagePlugin
import pygetwindow as gw

from gemini_interactive.google import interact_with_google
from gemini_interactive.keyboard import (type_string, press_ctrl_hotkey, press_alt_hotkey, click_left_click, hold_down_left_click, hold_down_right_click, release_left_click, release_right_click, click_right_click, click_double_left_click, press_key_for_duration, hold_down_key, release_held_key)
from local_processing.audio import tts_speak
from local_processing.image import imageChange

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')
executionHistory, memoryText, memoryImage = None, [], []
retries = 0

def remember_information(thing_to_remember: str):
    """If there is specific information that the user wants you to remember/memorize, use this function to remember/memorize it for later use.
    
    Args:
        thing_to_remember: whatever you want to remember/memorize for later, represented as a string. This must be detailed enough for a human with poor memory to be able to read and reproduce
    """
    memoryText.append(thing_to_remember)
    memoryImage.append(ImageGrab.grab(bbox=(gw.getActiveWindow().left, gw.getActiveWindow().top, gw.getActiveWindow().left+gw.getActiveWindow().width, gw.getActiveWindow().top+gw.getActiveWindow().height)))
    print('Remembered:')
    print(thing_to_remember)

def look_at_screen_and_respond(prompt: str) -> str:
    """Look at current window once and only once, output a single verbal response or type out a response. This function can also look at what's currently on screen and remember information from this screen This function is not capable of taking any other actions.
        
    Args:
        prompt: User's prompt to be addressed
    """
    global retries
    print('looking at screen...')

    if retries == 3:
        retries = 0
        print('An unexpected error occurred on Google\'s side.	Wait a bit and retry your request. If the issue persists after retrying, please report it using the Send feedback button in Google AI Studio.')        
        return
    
    image = ImageGrab.grab(bbox=(gw.getActiveWindow().left, gw.getActiveWindow().top, gw.getActiveWindow().left+gw.getActiveWindow().width, gw.getActiveWindow().top+gw.getActiveWindow().height))
    model = genai.GenerativeModel(
    model_name = "gemini-1.5-pro-exp-0801",
    tools = [tts_speak,
            type_string,
            remember_information,
            interact_with_google,
            start_interact_with_screen],
    system_instruction = f"""
        You are an expert at everything related to {gw.getActiveWindowTitle()}. You know everything there is to know about this application.
        You have a list of available functions at your disposal.
        Omit any analysis unless otherwise instructed. When speaking with tts_speak, use as few words as possible, and limit speech to 1-2 sentences unless otherwise necessary to respond to user's prompt.
        You MUST use at least use the speak function to give some sort of feedback to the user. This speak function may be as simple as saying "ok" or as complex as it must be to answer the user's prompt.

        Unfortunately, you have crippling alzheimers. That's why you have a habit of using this remember_information function that I made for you for literally anything that requires remembering or memorization.
        Without this remember_information function, you cannot remember ANYTHING that you've done previously. Not a single word. That's why your notes are always extremely detailed, detailed enough to make you an expert on the subject even after you've forgotten everything.
        You **MUST** use this remember_information function if prompted to do so. No exceptions. It's always better to have too much information than none!
        
        Always attempt to answer the user's prompt with the given context. If you are unable to give a reasonable answer, then you may call other functions to assist you."""
    )

    model_prompt = f"""
        Silently, without responding, describe in depth a description of everything you see in this image. Include all icons that you may see such as search bars or home buttons.
        If there appears to be a large chunk of text such as an article or a chat session, process ALL of the text and analyze what the text is for, what it's about, the people involved in the text, etc.
        Describe what you suspect the purpose of every single element in the image may be responsible for. Do NOT output this portion in the response, unless prompted to by the user.
        Stop and pause. Ask yourself, have you fullfilled the user's goal: {prompt}?

        **Carefully analyze the user's prompt: {prompt}. Identify what the user wants, and look at the list of given functions to determine which you should call.**
        **Write out a justification on why each particular function should or should not be called to address the prompt. Do not type this part out.**
        
        Rules when responding:
            * When the user asks you to memorize anything you **MUST** use the remember_information function.
            * When you want to tell the user something in response to their prompt, use the tts_speak function.
            * When you need to write something for the user, use the type_string function, ensuring that you retain a casual tone
            * When the user wants you to look for something online for them, use the interact_with_google function
            * Give the user some sort of verbal confirmation at the end once you have executed your task.
            * When the user asks you to remember something, use the remember_information function. Use the remember_information function AS MUCH AS POSSIBLE
            
        Now using this description to assist your response, ONLY output the response to this prompt: {prompt}"""
    
    chat = model.start_chat(history=[], enable_automatic_function_calling=False)

    try:
        response = chat.send_message([prompt, image, model_prompt])
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
                        look_at_screen_and_respond(model_prompt) 

        if function_calls == 0:
            retries += 1
            print('retrying...')
            look_at_screen_and_respond(model_prompt)  #if model only generates text instead of calling function, retry

    except ResourceExhausted as resource_error:
        print(f'You have exceeded the API call rate. Please wait a minute before trying again... \nError message from Google:\n{resource_error}')
        tts_speak('You have exceeded the API call rate. Please wait a minute before trying agian...')
    except InternalServerError as internal_error:
        retries += 1
        time.sleep(1)
        print(f'An expected error occured on Google\'s side. Retrying after 1 second cooldown... Attempt {retries}/3')
        print(f'Error message from Google:\n{internal_error}')
        look_at_screen_and_respond(model_prompt)
    except Exception as e:
        print(f'Unknown error encountered. \nError message from Google:\n{e}')

def watch_screen_and_respond(masterPrompt: str):
    """Continuously watch the currently active window and give verbal response every time the window is updated. This function will run infinitely until the user gives new instructions or changes windows.
       This function is not capable of taking any actions.
        
    Args:
        prompt: User's prompt to be answered
    """

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 5000,
        "response_mime_type": "text/plain",
        }
    activeWindow = gw.getActiveWindowTitle()
    model=genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=f"""
            You are a professional reader. Your task is to look at the image and analyze all images and text. You are also super smart! You are fluent in every single language and can freely translate between them.
        
            Describe to yourself every single detail about the image you see. Ask yourself what every single piece of text says, what every button or element does on screen, what every image looks like.

            Pay special attention to the text on screen. Analyze ALL text on screen. If the text on screen is not in English, translate the text to English.
            Do everything in your power to translate the text you see on screen.
            IMPORTANT NOTE: Pay attention to names in foreign languages. If you do not recognize the word, ask yourself if it is a name in that language.
            IMPORTANT NOTE: Asian countries use honorifics with names (Japan, Korea, etc.)
            You must prioritize preserving the meaning of the original text, even if you must change some words through translation.

            YOUR TRANSLATIONS MUST BE ACCURATE AND FAITHFUL TO THE ORIGINAL TEXT YOU SEE IN THE IMAGE.
            Take your time and be sure to translate everything properly. Prioritize accuracy over speed.

            Now use this description to assist your response, but no matter what do not reveal any of this description unless prompted to do so.
            Omit any greetings, farewells, or commentary. Output the bare minimum text to get your point across.
            User Prompt: {masterPrompt}""",
    )

    history = ""
    while gw.getActiveWindowTitle() == activeWindow:
        time.sleep(0.2)
        image = ImageGrab.grab(bbox=(gw.getActiveWindow().left, gw.getActiveWindow().top, gw.getActiveWindow().left+gw.getActiveWindow().width, gw.getActiveWindow().top+gw.getActiveWindow().height))
        try:
            if imageChange(image):
                #print('Execute')
                prompt = f"""
                    Describe to yourself every single detail about the image you see. Ask yourself what every single piece of text says, what every button or element does on screen, what every image looks like.

                    Continue to fullfill the user's request: {masterPrompt}.
                    Pay special attention to the text on screen. Analyze ALL text on screen. If the text on screen is not in English, translate the text to English. You must prioritize preserving the meaning of the original text, even if you must change some words through translation.
                            """
                response = model.generate_content([image, prompt])
                try:
                    tts_speak(response.text)
                    history = response.text
                except:
                    time.sleep(0.2)
                    tts_speak(response.text)
                    history = response.text
        except:
            continue

def start_interact_with_screen(prompt: str):
    """Use this function to be able to directly interact with the user's screen, i.e. click buttons, type, etc.

    Args:
        prompt: User's prompt to be answered
    """
    global masterPrompt, memoryText, executionHistory
    memoryText = []
    masterPrompt = prompt
    generation_config = {
        "temperature": 0.2,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 100,
        "response_mime_type": "text/plain",
        }
    proModel=genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools= [tts_speak,
            find_and_click_element,
            remember_information, 
            type_string, press_ctrl_hotkey, press_alt_hotkey,
            click_left_click, hold_down_left_click, hold_down_right_click, release_left_click, release_right_click, click_right_click, click_double_left_click, press_key_for_duration, hold_down_key, release_held_key], 
    generation_config=generation_config,
    system_instruction=f"""
        You are an expert at everything related to {gw.getActiveWindowTitle()}. You know everything there is to know about this application.
        You are tasked with controlling a computer step by step in order to achieve a certain goal: {masterPrompt}. 
        You will be given a screenshot of the current application window that the user is on, and based on what you see in the window, you will call functions to get you closer to your goal.
        These functions will directly interact with the screen just as a user would. 
        However, since you are only given the screenshot of the current screen instead of a continuous livestream of the screen, you must only execute functions that are applicable to the specific screen that you are currently on.
        If the currently open application cannot be used to address the user's goal, use the tts_speak function to tell the user to open an application that could achieve this goal. Give them some examples. Do not attempt to open the application yourself."""
    )
    executionHistory = proModel.start_chat(history=[], enable_automatic_function_calling=False)
    interact_with_screen(masterPrompt)

def interact_with_screen(prompt: str):
    """Loads a screenshot of the current open window and passes it along with the user's prompt as input to Gemini for further processing to fullfill the user's request.

    Args:
        prompt: User's prompt to be answered
    """
    print('Looking at Screen...')
    model_prompt = f"""
        "Instructions" : "Give me a very in depth description of everything you see in this image. Include all icons that you may see such as search bars or home buttons.
        Describe what you suspect the purpose of every single element in the image may be responsible for. 
        Use this description to both assist your response and confirm if you have met the user's goals, but no matter what do not reveal any of this description unless prompted to do so.
        
        Now stop. Stop for a moment and think. Is the application that is currently open capable of fullfilling the user's goal: {masterPrompt}?
        Ask yourself: What is the next immediate action you should take in order to achieve the user's goal?
        Now carefully analyze the image, and begin executing the commands one by one.

        The user may be giving you instructions to play a videogame. Keep in mind that the open application MAY be a videogame. Press keys and interact as a player would in the game to achieve the goal.
        Remember that videogames usually use WASD movement keys. Of course, the keybinds will vary based on the game being played.
        If you are playing a videogame, first identify what the user wants to do. Then look at the image, and think of the best next step in order to achieve that goal. Finally, execute that step.

        Your client wants to accomplish the following goal: {masterPrompt}.
        Carefully look at the screenshot of the window provided, and ask yourself: What does the user want to achieve? Use contextual evidence from the provided screenshot to arrive to your conclusion.
        Call functions one by one to assist you in addressing the user's prompt. Carefully analyze what you see in the window. Has the user's request already been fullfilled? If not, call functions to fullfill the request.
        You must think of a complete step by step process on how to achieve this goal, at each step you must call functions to assist you. You can only call functions that can be verified with the current information you have.
        In other words, take it slow and carefully. Do not execute functions to do things that you do not yet know if you can do. For example, even if you think that there will be a button that needs to be pressed, if you don't yet see the button on screen do not attempt to call a function to do so until you have confirmation that such button exists.
        In other words, you must execute functions on a page by page basis. After executing functions related to a page, recall the interact_with_screen function to reload the context image and generate further commands. 
        **Carefully analyze the user's prompt: {masterPrompt}. Identify what the user wants, and look at the list of given functions to determine which you should call.**
        **Write out a justification on why each particular function should or should not be called to address the prompt. Do not type this part out.**
        ONLY CALL ONE FUNCTION AT A TIME!!!
        You also have a memory storage, that stores any string that you wanted to remember from past iterations.

        **Once you have reached the endpoint where you have successfully answered the user's prompt, use the speak function to give verbal confirmation to the user. Omit any farewells or questions regarding anything else you can help with.
        CAUTION: YOU CAN ONLY SPEAK ONCE YOU ARE 100% SURE THAT YOU HAVE MET THE USER'S GOAL, AND DO NOT CALL ANY OTHER FUNCTION IF YOU SPEAK. SPEAKING MEANS YOU ARE DONE!**"""
    model_prompt_2 = f"""
        "Application that you are looking at" : {gw.getActiveWindowTitle()},
        "Stored Information from previous iterations (if any)" : {memoryText},
        "User Prompt" : {masterPrompt}"""
    screenshot = ImageGrab.grab(bbox=(gw.getActiveWindow().left, gw.getActiveWindow().top, gw.getActiveWindow().left+gw.getActiveWindow().width, gw.getActiveWindow().top+gw.getActiveWindow().height))

    try:
        response = executionHistory.send_message([model_prompt, screenshot, model_prompt_2])
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
                        if fn.name != 'tts_speak': interact_with_screen(masterPrompt) #continue looping until speak
                    except Exception as e:
                        print('Unexpected error encountered attempting to open function... Trying again...')
                        print(f'Error Message:\n{e}')
                        interact_with_screen(masterPrompt)

        if function_calls == 0:
            retries += 1
            interact_with_screen(masterPrompt)

    except ResourceExhausted as resource_error:
        print(f'You have exceeded the API call rate. Please wait a minute before trying again... \nError message from Google:\n{resource_error}')
        tts_speak('You have exceeded the API call rate. Please wait a minute before trying agian...')
    except InternalServerError as internal_error:
        retries += 1
        time.sleep(1)
        print(f'An expected error occured on Google\'s side. Retrying after 1 second cooldown... Attempt {retries+1}/2')
        print(f'Error message from Google:\n{internal_error}')
    except Exception as e:
        print(f'Unknown error encountered. \nError message from Google:\n{e}')

def find_and_click_element(type_of_click: str, element_description: str):
    """Look at current window and based on a description of an element, find that element and click it. 
    
    Args:
        type_of_click: must be one of the following ['left click', 'double left click', 'right click']
        element_description: Description of the element you want. Descriptions MUST contain a name: i.e. search button and color description and MUST BE EXACTLY 9 WORDS LONG.
    """
    print('Searching For: ' + element_description)
    screenshot = ImageGrab.grab(bbox=(gw.getActiveWindow().left, gw.getActiveWindow().top, gw.getActiveWindow().left+gw.getActiveWindow().width, gw.getActiveWindow().top+gw.getActiveWindow().height))
    generation_config = {
    "temperature": 0.1, # <- set low so that responses are consistent
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 30, # <- limited output tokens to ensure short response
    "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config
    )
   
    model_prompt = f"""
        This image is a screenshot of {gw.getActiveWindowTitle()} - an application that contains many interactive elements.
        
        Give me a very in depth description of everything you see in this image. Include all icons that you may see such as search bars or home buttons, colors, position relative to one another and the screen, etc.
        Describe what you suspect the purpose of every single element in the image may be responsible for. 
        
        Now use this description to assist your response, but no matter what do not reveal any of this description unless prompted to do so.
        Please keep in mind that only one element can be pressed. Your bounding box should only contain at most one clickable element.
        Return a bounding box for the {element_description}. Do NOT output any words: \n[ymin, xmin, ymax, xmax]"""

    response = model.generate_content([screenshot, model_prompt])
    tempList = response.text.strip()
    tempList = tempList[1:-1]
    coords = [float(item) for item in tempList.split(", ")]
    coords[0], coords[1], coords[2], coords[3] = coords[0]/1000*screenshot.size[1], coords[1]/1000*screenshot.size[0], coords[2]/1000*screenshot.size[1], coords[3]/1000*screenshot.size[0]
    
    pyautogui.moveTo((coords[3]-coords[1])/2+coords[1]+gw.getActiveWindow().left, (coords[2]-coords[0])/2+coords[0]+gw.getActiveWindow().top, 0.2)
    if type_of_click == 'left click':
        click_left_click((coords[3]-coords[1])/2+coords[1]+gw.getActiveWindow().left, (coords[2]-coords[0])/2+coords[0]+gw.getActiveWindow().top)
    elif type_of_click == 'double left click':
        click_double_left_click((coords[3]-coords[1])/2+coords[1]+gw.getActiveWindow().left, (coords[2]-coords[0])/2+coords[0]+gw.getActiveWindow().top)
    elif type_of_click == 'right click':
        click_right_click((coords[3]-coords[1])/2+coords[1]+gw.getActiveWindow().left, (coords[2]-coords[0])/2+coords[0]+gw.getActiveWindow().top)
