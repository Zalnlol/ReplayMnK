from time import sleep
import pyautogui
import os
import json
from pynput.mouse import Controller
from key_mappings import KEY_MAPPING


def convertKey(button):
    # Example: Key.F9 should return as F9, Button.left should return as left
    cleaned_key = button.replace('Key.','').replace('Button.','')
    if cleaned_key in KEY_MAPPING:
        return KEY_MAPPING[cleaned_key]

    return cleaned_key

def initializePyAutoGUI():
    pyautogui.FAILSAFE = True

def countdownTimer():
    #Countdown timer
    print("Starting" , end="")
    for i in range (0,5):
        print(".", end="")
        sleep(1)
    print("Go")

def playActions(filename):
    script_dir = os.path.dirname(__file__)
    filepath = os.path.join(script_dir, 'recordings', filename)
    with open(filepath, 'r') as jsonfile:
        data = json.load(jsonfile)

        #loop over each action
        for index, action in enumerate(data):
            #look for escape input to exit
            if action['button'] == 'Key.esc':
                break

            #perform the action
            if action['type'] == 'keyDown' or action['type'] == 'keyUp':
                key = convertKey(action['button'])
                if action ['type'] == 'keyDown':
                    pyautogui.keyDown(key)
                elif action ['type'] == 'keyUp':
                    pyautogui.keyUp(key)

            if action['type'] == 'mousePress':
                key = convertKey(action['button'])
                position = action['position']
                
                # Move mouse to the position
                pyautogui.moveTo(position[0], position[1], duration=0.1)
                
                # Press mouse button
                pyautogui.mouseDown(button=key)
            
            elif action['type'] == 'mouseRelease':
                key = convertKey(action['button'])
                position = action['position']
                t1 = action['time']
                t0 = data[index - 1]['time']
                deltaTime = t1-t0
                # Move mouse to the position
                pyautogui.moveTo(position[0], position[1], duration=deltaTime)
                
                # Release mouse button
                pyautogui.mouseUp(button=key)
            try:
                next_action = data[index + 1]
                print(next_action)
            except IndexError:
                break
            elapsed_time = next_action['time'] - action['time']
            if elapsed_time >= 0:
                sleep(elapsed_time)
            else:
                raise Exception('unexpected action ordering.')
            

def main():
    initializePyAutoGUI()
    countdownTimer()
    playActions("actions_test_01.json")

if __name__ == "__main__":
    main()