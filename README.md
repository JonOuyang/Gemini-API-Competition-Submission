# Introducing Jayu
A next generation AI Personal Assistant, fully powered by Google Gemini

## What is Jayu?
Jayu is a an AI personal assistant that takes inspiration from the popular assistant Siri, and inspiration from the all powerful assistant Jarvis from Iron Man. Using the Google Gemini API, Jayu aims to bridge the gap between reality and fiction, giving the term "personal assistant" a new meaning. Jayu's purpose is to make the lives of users easier than ever before, with new capabilities and accessibility everywhere.

## What can Jayu do?
Jayu is powered by Google Gemini Pro, Flash, and Vision, which allows Gemini to act both as a LLM and VLM. Utilizing these capabilities, Jayu can:
- Directly access the user's current active window in order to execute tasks
- Directly type on the currently selected text box of ANY application
- Assist users by analyzing information (textual or visual) on screen and responding with context in mind
- Memorize information temporarily and use later on command
- Listen to user (on wakeword command) and give verbal feedback
- Use gesture recognition to scroll up and down scrollable elements

Naturally, this is a non-extensive list of Jayu's capabilities. Being powered by Gemini, Jayu is capable of doing everything Gemini is capable of along with the aforementioned abilities. Jayu is capable of long text generation, image analysis, etc.

## Safety and Security Acknowledgement
The idea of an AI having access to one's screen is very dangerous. Here's what we have to say about that:

- Jayu does NOT retain any information between sessions. Jayu does NOT utilize any sort of database for the reason of security. ALL information is stored locally in python variables.
- All screenshots of user's current active screen is stored locally in python variables using the computer vision library Pillow (PIL). These images are passed along with prompts to the Gemini API. No screenshots are saved besides this.
- Jayu is only capable of looking at the ACTIVE window. Jayu does NOT have access to anything else on screen. Jayu does NOT have access to files on the computer. Jayu does NOT have access to the terminal or powershell or any sort of command line UNLESS the user opens it and commands Jayu to assist.
- Jayu is ONLY capable of looking on screen when the user prompts it to do so. It will only take a screenshot of the current window for analysis after every function execution cycle internally. In other words, Jayu does record the screen.
- Speech to Text capabilities are powered by the python library RealtimeSTT. All recordings are stored and processed locally in python and no speech is remembered between sessions. While RealtimeSTT technically actively listens, all speech is processed in real time and immediately forgotten if the wakeword "Hey Gemini" is not used. Only the immediate prompt following the wakeword is stored in a variable, which is immediately wiped after execution is complete. 

ALL code for Jayu is publically available in this repository. Feel free to disable specific functions.

## API Usage
Jayu depends on only 2 APIs.
1. The primary API is Google Gemini API. Text prompting uses Gemini 1.5 Flash, while Image prompting uses Gemini 1.5 Pro restrictively.
2. The second API used is elevenlabs API for text to speech synthesis. ellevenlabs is a free (but limited) AI generated text to speech service. This API is optional, as it is not needed for the core functionalities of Jayu.
 
## Who created Jayu?
Jayu was created by Jonathan Ouyang independently for the Google Gemini API Competition. However, after the competition submission deadline this repository was made public for others to contribute. 
