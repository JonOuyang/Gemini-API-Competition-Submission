import os
import time

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from local_processing.audio import tts_speak

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

options = Options()
options.add_experimental_option("detach", True) #ensure window stays open
options.add_argument('log-level=3')
chat, driver, masterPrompt = None, None, None
visited_links = []
elements = None #current webpage's elements

# Function that returns current active driver for cross-file usage
def getDriver():
    return driver

def interact_with_google(search: str):
    """Access anything or any page on the web; This function takes in the user's request and identifies keywords to search google or open websites to look up information
    
    Args:
        search: Repeat exactly word for word what the user asked from you. Include every single part of their input.
    """
    global driver, masterPrompt
    masterPrompt = search

    #checks if driver already exists, use existing driver if available, otherwise continue
    try:
        driver.current_url 
        scan_current_window_html(masterPrompt)
    except:
        driver = webdriver.Chrome(options=options)
        generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 100,
        "response_mime_type": "text/plain",
        }
        model=genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools= [search_google, search_link], 
        generation_config=generation_config,
        system_instruction="""You are a super tech savy teenager helping their elderly parent do something online."""
        )
        soloChat = model.start_chat(history=[], enable_automatic_function_calling=True)
        model_prompt = f"""
            The prompt is: {search}
            You open google and see the search function. You will use the search_google function to search google using keywords of your choice.
            You only get one search so search a phrase that will get you as close to answering the prompt as possible.
            This phrase can be as long or as short as needed to effectively search for something.
            Examples include:
                Prompt: Find me articles on how to build a snowman
                Search: how to build a snowman

                Prompt: Open up google
                Search: use search_link function to directly search https://www.google.com/

                Prompt: Find me information on the newest Minecraft release
                Search: Minecraft Recent Release Patch Notes

            If you know the exact link for the website you want to pull up, (i.e. widely known websites like YouTube, Google, Gmail), you may use the search_link function and search the link directly.
            YOU MUST SEARCH ONCE AND ONLY ONCE USING EITHER THE SEARCH GOOGLE OR SEARCH LINK FUNCTION"""
        soloChat.send_message(model_prompt)

def extract_elements(html_content):
    """ Given the full HTML of a webpage, extract ALL text and links that may appear, preserving the ordering. Also filters out miscellaneous gibberish
        
    Args:
        html_content: full webpage HTML
    """
    print('extracting elements...')
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_elements = 'The title of the page that is currently open is: ' + driver.title + '\nThe link to the page that is currently open is ' + driver.current_url + "\n"
    for element in soup.descendants:
        if isinstance(element, str) and element.strip() and element.parent.name not in ['script', 'noscript', 'template', 'style']:  # Get text nodes
            extracted_elements += f"HTML Element Tag: <{element.parent.name}>. Text: {element.strip()}\n"
        elif element.name == 'a' and (element.has_attr('href') or element.parent.name in ['link']) and len(element.get('href')) > 8:  # Get links
            extracted_elements += f"\nLink (href or url): {element.get('href')} - This link is very likely related to the text in adjacent indices, try looking at them and finding correlation\n\n"

    return extracted_elements

def scan_current_window_html(prompt: str):
    """ If the user's prompt cannot be answered using the current information extracted from the current chrome page, then this function can be called to re-read the html of the page.
    Extracts the full html of a chrome browsing page and parses it using Gemini LLM in order to identify elements that are helpful to addressing the user's prompt.
        
    Args:
        prompt: the prompt that must be answered
    """
    global chat, driver
    try:
        driver.current_url
    except:
        print('Error: window no longer open')
        return
    print(f'interact with chrome called with prompt: {prompt}')
    if not driver:
        driver = webdriver.Chrome(options=options)
    availableTools = [search_google, search_link, tts_speak, go_back]

    print('Elements is empty') if not elements else print('Elements contains information: Length '+str(len(elements)))
    generation_config = {
    "temperature": 0.5, # <- set to 0 for less variation
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 500,
    "response_mime_type": "text/plain",
    }
    model=genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=availableTools, 
    generation_config=generation_config,
    system_instruction="""
        You are a super tech savy teenager helping their elderly parent do something online.
        When responding, use as few words as possible, and limit speech responses to 1-2 sentences unless otherwise necessary to respond to user's prompt.
        Your responses are linked to another function that will be directly called. What this means is that if you are asked for a link or button element, respond with ONLY the link or element, as this will be passed as an argument for another function.
        Omit any analysis unless otherwise instructed.
        You will recieve a trimmed version of the current website's html code, so that the input only contains text and links visible to the user.
        The input will be in the format: HTML Element Tag: tag. Text: text.
        Note that while the full html code is not shown, ALL ELEMENTS REMAIN IN CHRONOLOGICAL ORDER. What this means is that elements that are located near each other are most likely associated with one another in some way.
        Also be aware of the patterns that you see in the given text. While not shown, repeated patterns can suggest a list formatting on the webpage.
        Do not use the speak command unless absolutely necessary.
        Try to utilize the search_link function rather than the search_google function.
        When you are ready to answer the user's prompt, use the speak function.
        When you use the speak function, speak as if you are a human talking to another human. Speak naturally."""
    )

    if not chat:
        chat = model.start_chat(history=[], enable_automatic_function_calling=False)
    
    model_prompt = f"""
        "User Prompt" : {prompt},

        "Instructions" : 
            "Carefully analyze the following information adhering to the system instructions set in place, and attempt to answer the user prompt.
            Pay attention to the following details: 
            - What website are you currently on? What's the name of it? What's the relation between the current page and what the user wants?
            - What information does this website tell you? Can you answer the user's prompt using the information curretly listed here?
            - Could you give a response right now that a human would be able to understand in response to the prompt?
            - look at the chat history. When generating your response, ask yourself: is this action/thought redundant? Avoid redundancy. Choose to explore.
            - Pay attention to the link and the webpage. Is the user asking for an article? If so, it woulnd't make sense to go to youtube. Is the user asking for a video? It would make sense to explore youtube links. 
            - Look at ALL text and link given in the Scraped Data. Compare the information you have to one another, and make informative choices on which function to call or what to tell the user. 
            DO NOT SAY ANY PART OF YOUR THOUGHT PROCESS. This is simply for you to consider and to guide your thought process. 
            If and only if you are unable to answer with the given information from the current webpage, call functions to assist you in looking for the information. 
            If you can directly answer the user's prompt, use the speak function ONCE to tell the user your answer or to tell the user that you are done. After using the one speak command to inform the user you must NOT call any more functions including another speak function.",
        
        "Scraped Data from Current Website (chronological)" : {elements},
        
        "Blacklisted Links" : {visited_links},
        
        "Rules when responding" :  
            "YOU MAY ONLY CALL ONE FUNCTION. Ask yourself if you've answered the user's request. If yes, you're done.
            Look at the scraped data and attempt to answer the user's question. If it cannot be answered, begin calling functions to assist you with searching for information.
            If the user is commanding something rather than asking a question, look at the current information and link and ask yourself: is this what the user asked for? If so, confirm with the speak command, ONLY USE THE COMMAND ONCE, and exit.
            If you are prompted you MUST return at least once function to execute, if the task is complete use the speak function.
            If the speak function is called that means you have successfully completed the task and you ABSOLUTELY MUST NOT CALL ANOTHER FUNCTION AFTERWARDS. THE SPEAK FUNCTION MUST BE THE LAST FUNCTION TO BE CALLED;
            Pay attention to the link and the webpage. Is the user asking for an article? If so, it woulnd't make sense to go to youtube. Is the user asking for a video? It would make sense to explore youtube links. 
            You are NOT permitted to say that you cannot find any information. Use all available functions strategically to find the answer, but prioritize clear and concise responses based on the information available. 
            Respond heuristically. You only need to provide an answer good enough to satisfy a human. However, your answer must still be specific.
            Ask yourself if you've answered the user's request. If yes, you're done, and use the speak function to verbally affirm that you have completed the task.
            If you require the user to sign in to a website, or if the website requires a Captcha or for the user to verify that they are human, let the user know and ask them to sign in or complete the verification. Only ask the user if you are very confident that the information needed lies behind this webpage."
            If you call the search_link command, make sure that the argument is a full link. Many of the links listed in the elements is in the form of an href. Be careful and infer the full link if given an href."""

    print('Analyzing and retrieving model response....')
    print()
    try:
        response = chat.send_message(model_prompt)
    except:
        print('Something went wrong.... Trying again...')
        time.sleep(1)
        scan_current_window_html(prompt)
    
    for part in response.parts:
        if fn := part.function_call:
            if callable(globals().get(fn.name)):
                try:
                    func = globals()[fn.name]
                    kwargs = fn.args
                    func(**kwargs)
                except:
                    print(f'Error encountered attempting to open function: Function: {func}, Args: {fn.args}')
            else:
                print('Error calling function...')

def search_google(search_keyword: str):
    """Use the Google search engine to search up keywords. Only use if absolutely necessary. Otherwise, attempt to explore links
        
    Args:
        search_keyword: phrase to be searched for on Google
    """
    global elements
    print(f'search google called with keyword: {search_keyword}')
    link = f"https://www.google.com/search?q={search_keyword}"
    visited_links.append(link)
    driver.get(link)
    elements = extract_elements(driver.page_source)
    scan_current_window_html(masterPrompt)

def search_link(link: str):
    """Go to a link. This link can NOT be an href. 
        
    Args:
        link: the link to the webpage in the form of a string
    """
    global elements
    print(f'Searching link: {link}')
    visited_links.append(link)
    driver.get(link)
    elements = extract_elements(driver.page_source)
    scan_current_window_html(masterPrompt)

def go_back(num_pages: int):
    """If not enough information can be found on the current page, use this function to move backward in browser's history
    
    Args:
        n: number of times to go back (i.e. n=1 means go back 1 page, n=2 means go back 2 pages)
    """
    count = 0
    while count < num_pages:
        driver.back()
    scan_current_window_html(masterPrompt)
