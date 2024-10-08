# Introducing Jayu

More than a chatbot. More than data analysis. More than an LLM. The real life Jarvis. Powered completely by Google Gemini. **WELCOME, JAYU**

See our demo video HERE: https://www.youtube.com/watch?v=shnW3VerkiM 

## What Exactly is Jayu?
Jayu is a an AI personal assistant that takes inspiration from the all powerful assistant Jarvis from Iron Man. Using the Google Gemini API, Jayu aims to bridge the gap between reality and fiction, giving the term "personal assistant" a new meaning. Jayu's purpose is to make the lives of users easier than ever before, with new capabilities and accessibility everywhere.

Jayu is a pure python script that can run in the background of your computer while you do anything else on your desktop. It can see any window that you currently have open and active, and it can open its own chrome window to answer prompts. Jayu can manipulate current active windows as it sees fit using mouse movements and clicks, but cannot open apps on its own.

![Jayu Diagram (2)](https://github.com/user-attachments/assets/d4545d47-3ece-438d-a891-a6d85d97fe22)

**Please take a moment to look at these [important findings](https://github.com/JonOuyang/Gemini-API-Competition-Submission/blob/main/PROJECT_NOTES.md) that form the foundations of many of the features of Jayu.**

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

### What exactly does Jayu have access to?
- Jayu is only capable of looking at the ACTIVE window. Jayu does NOT have access to anything else on screen, including other open windows or processes. 
- Jayu does NOT have access to files on the computer. Jayu does NOT have access to the terminal or powershell or any sort of command line UNLESS the user opens it and commands Jayu to assist.
- Jayu is ONLY capable of looking on screen when the user prompts it to do so. It will only take a screenshot of the current window for analysis after every function execution cycle internally. In other words, Jayu does not record the screen.

### What kind of information does Jayu store?
- Jayu does NOT retain any information between sessions.
- Jayu does NOT utilize any sort of database for the reason of security. ALL information is stored locally in python variables.
- All screenshots of user's current active screen is stored locally in python variables using the computer vision library Pillow (PIL). These images are passed along with prompts to the Gemini API. No screenshots are saved besides this.
- Speech to Text capabilities are powered by the python library RealtimeSTT. All recordings are stored and processed locally in python and no speech is remembered between sessions. While RealtimeSTT technically actively listens, all speech is processed in real time and immediately forgotten if the wakeword "Hey Gemini" is not used. Only the immediate prompt following the wakeword is stored in a variable, which is immediately wiped after execution is complete.

### Regarding concerns on camera access for gesture recognition...
- Gesture recognition is powered by mediapipe and opencv. While it uses your camera to see your hands, the camera footage is NOT sent to Google Gemini for processing. All processing is done locally within the script itself. When we say "Jayu" is capable of gesture recognition, gesture recognition is a feature of Jayu. It is not a feature of Google Gemini. Google will not see your person unless you literally command Gemini to look at your screen and look at a screenshot of yourself.
- The computer's camera is NOT connected to the Gemini pipeline. In other words, Google Gemini is quite literally unable to ever use your camera.

ALL code for Jayu is publically available in this repository. Feel free to disable specific functions.

## How to run Jayu

For easiest installation, I recommend using Windows operating system. You will likely run into issues running this on macOS due to some libraries requiring the x86 architecture. Both Windows and Linux run x86.

1. Clone the Github repository
```bash
git clone https://github.com/JonOuyang/Gemini-API-Competition-Submission
```
2. Navigate to the project directory and install the required dependencies
```bash
pip install -r requirements.txt
```
NOTE: Depending on the environment and operating system you try to run the project on, you may have to take extra steps in installation. Please see the respective library documentations in that case.

3. Go to the .env folder and replace the placeholder values with your Gemini and elevenlabs API keys and elevenlabs URL. 

4. Run the main.py file
```bash
python main.py
```
NOTE: Due to the various dependencies, please allow the program about 40 seconds to complete loading all files (especially the gesture recognition and audio processing files)

## API Usage
Jayu depends on only 2 APIs.
1. The primary API is Google Gemini API. Text prompting uses Gemini 1.5 Flash, while Image prompting uses Gemini 1.5 Pro.
2. The second API used is elevenlabs API for text to speech synthesis. ellevenlabs is a free (but limited) AI generated text to speech service. This API is optional, as it is not needed for the core functionalities of Jayu.
 
## Who created Jayu?
Jayu was created by Jonathan Ouyang independently for the Google Gemini API Competition. However, after the competition submission deadline this repository was made public for others to contribute. 
Questions? Contact me at: jonsouyang@ucla.edu
