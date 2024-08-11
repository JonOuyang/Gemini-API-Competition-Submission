from enum import Enum
import keyboard
import pyautogui
import pygetwindow as gw
import time

IDE = [
    "Visual Studio Code", "PyCharm", "Sublime",
    "Atom", "IntelliJ", "Thonny",
    "IDLE",  "Jupyter Notebook", "Vim",
    "Emacs", "Brackets", "Komodo IDE",
    "Eclipse", "NetBeans", 'XCode',
    'CLion', 'Spyder', 'Wing'
]

def type_string(string: str): #work in progress
    """Types out a string

    Args:
        string: The argument should be passed as a multiline string
    """
    # manual backslash error reassignment
    # NOTE: we can NOT use .replace('\\', '\') because \\ is the floor operator in python
    string = string.replace("\\'", "\'")
    string = string.replace('\\\\', '\\')
    string = string.replace('\\n', '\n')
    string = string.replace('\\r', '\r')
    string = string.replace('\\t', '\t')
    string = string.replace('\\b', '\b')
    string = string.replace('\\f', '\f') 

    # check if current window supports auto indentation. if it does, remove indentation
    for name in IDE:
        if name.lower() in gw.getActiveWindowTitle().lower():
            string = str("".join([i for i in string if i != '\t']))
            break
    
    #print('RAW STRING: ' + repr(string))
    keyboard.write(string, delay=0.01)
    keyboard.press_and_release('enter', 'enter')

def click_left_click(x: float, y: float):
    """Emulates a mouse left click
    
    Args:
        x: x coordinate on screen of where you want to click
        y: y coordinate on screen of where you want to click
    """
    pyautogui.click(x=x, y=y, clicks=1, button='left')

def hold_down_left_click(x:float, y:float):
    """Emulates a mouse held down left click
    
    Args:
        x: x coordinate on screen of where you want to click
        y: y coordinate on screen of where you want to click
    """
    pyautogui.mouseDown('left')

def hold_down_right_click(x:float, y:float):
    """Emulates a mouse held down left click
    
    Args:
        x: x coordinate on screen of where you want to click
        y: y coordinate on screen of where you want to click
    """
    pyautogui.mouseDown('right')

def release_left_click(x:float, y:float):
    """Emulates releasing the mouse left click button
    
    Args:
        x: x coordinate on screen of where you want to click
        y: y coordinate on screen of where you want to click
    """
    pyautogui.mouseUp('left')

def release_right_click(x:float, y:float):
    """Emulates releasing the mouse left click button
    
    Args:
        x: x coordinate on screen of where you want to click
        y: y coordinate on screen of where you want to click
    """
    pyautogui.mouseUp('right')

def click_double_left_click(x: float, y: float):
    """Emulates a mouse double (left) click
    
    Args:
        x: x coordinate on screen of where you want to click
        y: y coordinate on screen of where you want to click
    """
    pyautogui.click(x=x, y=y, clicks=2, interval=0.1, button='left')

def click_right_click(x: float, y: float):
    """Emulates a mouse right click
    
    Args:
        x: x coordinate on screen of where you want to click
        y: y coordinate on screen of where you want to click
    """
    pyautogui.click(x=x, y=y, clicks=1, button='right')

def press_key_for_duration(key: str, seconds: float) -> None:
    """Holds down a key for a specified duration (This function is useful for simulating an individual short key presses)
    
    Args:
        key: The key to be pressed down. Can be any alphanumeric key on the keyboard
        seconds: The amount of time to be pressed down in seconds
    """
    pyautogui.keyDown(key)
    time.sleep(seconds)
    pyautogui.keyUp(key)
    print(f'Key chosen: {key}')
    print(f'Key held down for {seconds}s')

def hold_down_key(key: str) -> None:
    """Press down a key indefinitely until otherwise told, emulating the user holding down a key
    
    Args:
        key: The key to be pressed down. The key must be one of the following 'w', 'a', 's', 'd'
    """
    pyautogui.keyDown(key)

def release_held_key(key: str) -> None: #may need to add key held memory
    """Release a previously held down key, emulating the user releasing a held down key
    
    Args:
        key: The key to be pressed down. The key must be one of the following 'w', 'a', 's', 'd'
    """
    pyautogui.keyUp(key)

def press_ctrl_hotkey(key: str):
    """Press down a key along with the control key to emulate a hotkey
        
    Args:
        key: The key to be pressed along with control
    """
    pyautogui.hotkey('ctrl', key)

def press_alt_hotkey(key: str):
    """Press down a key along with the alt key to emulate a hotkey
        
    Args:
        key: The key to be pressed along with control
    """
    pyautogui.hotkey('alt', key)