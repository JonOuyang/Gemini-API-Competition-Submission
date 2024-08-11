# JAYU Project Notes

It wasn't easy getting to this point. I went through a LOT of trial and error to get Gemini to respond exactly how I wanted it to. So here's an extensive list of every single trick in the book I used.

# Handling Various Gemini-side Errors
### The Infinite Loop Error
**Problem:** I noticed that when using the **automatic function calling** feature of Gemini, it would often end up in an infinite loop of function calls. This was strange, because when I printed out the raw json output from Gemini, it would state that it only intended to call 1 or maybe 2 functions. The functions called didn't actually execute the function, and would result in infinite and repeated blank outputs.
**Solution:** I had to switch to MANUAL function calling, which solved the problem. The basic code for this can be found in the google.py, screen.py, and main.py files

### The Recitation Error
**Problem:** Sometimes Gemini would return a "Recitation" error when called on tasks. For example, my test case was "Hey Gemini, can you write me a python function for bubble sort?" We know that Gemini is absolutely capable of doing so, and it works perfectly fine in the web version and in API studio. So what was the problem?
**Solution:** It turns out that function calling is an extremely delicate process. The issue was resolved by shortening the description of the functions (see API cookbook to see what a description would look like). Also noticed that on occasion some specific words would trigger this Recitation error, although I don't remember off the top of my head what they were. It is important to keep the description as concise as possible, leaving out any unnecessary information.

### The 500 Google-side Error
This problem has been unsolved. This error appears to be somewhat random, as re-running prompts can sometimes fix this error. I do notice that this error happens on more compelx task prompts than simple ones. For example, telling Gemini to "introduce yourself" will almost never result in this error, but something more complex such as "look at my screen and using my open Spotify window find me some songs from Hamilton and play me one of them."

# General Prompting Techniques

### Accurate Function Calling
Gemini on its own is not very good at identifying exactly what functions to call. You have to quite literally tell Gemini **how** to think. So we include this specific phrase in the prompt:

```
**Carefully analyze the user's prompt: {user_prompt}. Identify what the user wants, and look at the list of given functions to determine which you should call.**
**Write out a justification on why each particular function should or should not be called to address the prompt. Do not type this part out.**
```

What this does is it forces Gemini to actually acknowledge every single one of its options and evaluate them against one another. 

Other Notes on Prompting:
- JSON formatted prompts have minimal effect
- Bolding and spacing have minimal effect
- the longer the prompt the harder it is for Gemini to listen to instructions

### The External Memory Function
Gemini, being a very large and very capable LLM, is very reluctant to use a "memory function," because Gemini believes that it is more than capable of remembering the information itself. So the workaround that I found was to essentially use prompting and tell Gemini that it was a **"super smart AI that has crippling alzheimers."**

```
Unfortunately, you have crippling alzheimers. That's why you have a habit of using this remember_information function that I made for you for literally anything that requires remembering or memorization.
Without this remember_information function, you cannot remember ANYTHING that you've done previously. Not a single word. That's why your notes are always extremely detailed, detailed enough to make you an expert on the subject even after you've forgotten everything.
You **MUST** use this remember_information function if prompted to do so. No exceptions. It's always better to have too much information than none!
```

# Computer Vision Techniques

### General Computer Vision
Gemini Flash is **incompetent** when it comes to Computer Vision.
Gemini Pro is **better**, but it takes some very specific prompting to get it to work.

After many tests, I found that Gemini Pro responds much better when you explicitely tell it:

```
Give me a very in depth description of everything you see in this image. Include all icons that you may see such as search bars or home buttons.
Describe what you suspect the purpose of every single element in the image may be responsible for. 
```

I'm not exactly sure what this does on an internal level, but I presume this forces Gemini to slow down and actually look more closely at the image.

### Object Detection
One of Jayu's main strengths is its use of Gemini Computer Vision to interact with the screen. It does so using Object Detection. Given a description of an object, Gemini Pro looks through the screenshot of the open window and finds the object and returns the (x, y) coordinate of the center. 
Just like Before, we tell Gemini explicitely to look through and describe every single element or icon it sees. This helps it get an idea of what is ACTUALLY on the screen.

Now here's the important part. Keep your descriptions short. Gemini is the one creating the description, and Gemini is the one using that description to find elements. Our solution was to explicitely tell Gemini to **limit its descriptions to 7 words, including the name of the element and relative position if possible**. Longer descriptions actualy hurt Gemini's ability to detect objects, while short 1 or 2 word inputs don't give Gemini enough information to reliably and accurately locate it. This finding needs to be studied more, and I hope that Google themselves will be able to improve Gemini's Computer Vision abilities. 

# Design Optimization
### Constant Watching
Notice how Jayu has a function to constantly watch your screen to give continuous feedback. Calling the Gemini API periodically would be VERY expensive and a waste. So what I did instead was create a function that essentially takes a screenshot of your screen every 0.2 seconds and compares it to the previous screenshot. When it detects any sort of change in the screen, it will begin paying attention. There is also a built in similarity function, that takes 2 screens and compares them to one another. There is a certain threshold that has to be met in order for the new screenshot to be considered different to the old one. For example, if you scroll 3 pixels down on a page, it won't be considered a "new" screenshot, therefore it will be ignored by the system. If you scroll a substantial amount, the function will begin paying attention and start a countdown whenever it notices that you STOP scrolling. This countdown is approximately 0.8 seconds (if i remember correctly), and after this countdown is over it will send the screenshot to a Gemini Pro model for analysis and processing

### Chrome Browsing
Gemini is capable of interpreting full HTML of websites. However, some websites, for example the Google search page, contain too much HTML and does not fit within Gemini's 2M context window. Therefore, we extract all of the text AND links available on the site, use a function to preprocess and clean the data and add aditional labels "Text" or "Link", and feed it into Gemini. We then tell Gemini to look for consistent patterns throughout the scraped information, and use these patterns to deduce what the links do and whatnot. 
