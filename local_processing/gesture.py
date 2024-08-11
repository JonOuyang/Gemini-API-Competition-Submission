import cv2
import mediapipe as mp
import pyautogui

#This will take about 20 seconds to properly boot up...
vid = cv2.VideoCapture(0)
cv2.setNumThreads(0)
vid.set(3, 1280)
mphands = mp.solutions.hands
Hands = mphands.Hands(max_num_hands= 2, min_detection_confidence= 0.7, min_tracking_confidence= 0.6 )
mpdraw = mp.solutions.drawing_utils
handtrack = {}

# Scroll up or down, using a loop for smoother effect
def scroll(direction: str):
    if direction == 'up':
        for _ in range(10):
            pyautogui.scroll(100)
    elif direction == 'down':
        for _ in range(10):
            pyautogui.scroll(-100)

# Function to calculate the slope formed by the average of pointer and middle finger to wrist
def slope(p2, p1) -> float:
    mult = 1 if p2[0] < p1[0] else -1 #force angles to be positive if pointing upward, negative for downward
    if p2[0] - p1[0] == 0: return float('inf') * mult
    else: return (p2[1] - p1[1])/(p2[0]-p1[0]) * mult

# Function to process slopes and recognize gestures heuristically 
def watchGesture(id, angle):
    global handtrack, start, stop
    #count the number of frames between key frames
    if id not in handtrack:
        handtrack[id] = []
    else:
        handtrack[id].append(angle)
        if len(handtrack[id]) > 60:
            handtrack[id].pop(0)

    # find if starting value exists -> fingers at neutral position at beginning
    for hand in handtrack:
        start, peak, stop = None, None, None
        for i in range(len(handtrack[hand])):
            if handtrack[hand][i] < 1.0 and handtrack[hand][i] > -0.8:
                start = i
                break
            
        # if starting value exists, find end value -> fingers at neutral position at end
        if start != None:
            for i in range(len(handtrack[hand])-1, start, -1):
                if handtrack[hand][i] < 1.0 and handtrack[hand][i] > -0.8:
                    stop = i
                    break

        # if start and end values exist, find if slopes pass threshold to be recognized as gesture
        if start != None and stop != None:
            for i in range(start, stop):
                if handtrack[hand][i] > 2:
                    peak = 1
                    break
                elif handtrack[hand][i] < -1.0:
                    peak = -1
                    break
        else:
            continue
        
        # identify whether the gesture is up or down if all start, stop, and peak exist
        if start != None and peak != None and stop != None:
            if peak == 1:
                scroll('up')
                handtrack[hand] = []
            elif peak == -1:
                scroll('down')
                handtrack[hand] = []

# Function to actively watch and process every single frame from camera, and send slope data to watchGesture() to recognize gestures 
def infiniteGestureWatch():
    global vid, mphands, Hands, mpdraw, handtrack
    while True:
        _, frame = vid.read()
        RGBframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = Hands.process(RGBframe)
        if result.multi_hand_landmarks:
            for count in range(len(result.multi_hand_landmarks)):
                handLm = result.multi_hand_landmarks[count]
                zeroPoint = None
                for id, lm in enumerate(handLm.landmark):
                    h, w, _ = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if id == 0:
                        zeroPoint = (cx, cy)
                    elif id == 8:
                        pfSlope = slope((cx, cy), zeroPoint)
                    elif id == 12:
                        mfSlope = slope((cx, cy), zeroPoint)
                watchGesture(count, (pfSlope +mfSlope)/2)