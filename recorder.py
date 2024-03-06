from pynput import mouse, keyboard
from time import sleep, time
import json
import datetime
import os

OUTPUT_FILENAME = 'actions_test_01'

#declare mouse_listener globally so that keyboard on_release can stop it
mouse_listener = None

#declare our start_time globally so that the callback functions can be reference it
start_time = None

#keep track of unreleased keys to prevent over-reporting press events:
unreleased_keys = []


unreleased_mouse = []

#storing all input events
input_events = []

class EventType():
    KEYDOWN = 'keyDown'
    KEYUP = 'keyUp'
    # CLICK = 'click'
    MOUSE_PRESS = 'mousePress'
    MOUSE_RELEASE = 'mouseRelease'


def main():
    sleep(3)
    runListeners()
    print(seconds_to_time(elapsed_time()))
    global input_events
    print(json.dumps(input_events))

    script_dir = os.path.dirname(__file__)
    filepath = os.path.join(script_dir, 'recordings', f'{OUTPUT_FILENAME}.json')
    with open(filepath, 'w') as outfile:
        json.dump(input_events, outfile, indent = 4)

def seconds_to_time(seconds):
    # Convert seconds to a timedelta object
    td = datetime.timedelta(seconds=seconds)

    # Convert the timedelta object to a string in the format HH:MM:SS.mmmmmm
    time_str = str(td)

    # If the length of the string is less than 12 characters, pad it with zeros
    if len(time_str) < 12:
        time_str = "0" * (12 - len(time_str)) + time_str

    # Replace the microsecond separator with a colon
    time_str = time_str.replace('.', ':')

    # Return the formatted time string
    return time_str

def record_event(event_type, event_time, button, position = None):
    global input_events
    input_events.append({'time':event_time,
                         'type':event_type,
                         'button':str(button),
                         'position':position})
    
    if event_type == EventType.MOUSE_PRESS:
        print(f'{event_type} on {button} position {position} at {"%1.2f" % event_time}')
    elif event_type == EventType.MOUSE_RELEASE:
        print(f'{event_type} on {button} position {position} at {"%1.2f" % event_time}')
    else:
        print(f'{event_type} on {button} at {"%1.2f" % event_time}')



def on_press(key):
    # we only want to record the first keypress event until that key has been released
    global unreleased_keys
    if key in unreleased_keys:
        return
    else:
        unreleased_keys.append(key)

    try:
        record_event(EventType.KEYDOWN, elapsed_time(), key.char)
    except AttributeError:
        record_event(EventType.KEYDOWN, elapsed_time(), key)

def on_release(key):
    # mark key as no longer pressed
    global unreleased_keys
    try:
        unreleased_keys.remove(key)
    except ValueError:
        print('ERROR: {} not in unreleased_keys'.format(key))
    try:
        record_event(EventType.KEYUP, elapsed_time(), key.char)
    except AttributeError:
        record_event(EventType.KEYUP, elapsed_time(), key)
        

    if key == keyboard.Key.esc:
        # Stop mouse listener
        global mouse_listener
        mouse_listener.stop()
        # Stop keyboard listener
        raise keyboard.Listener.StopException
    
def on_click(x, y, button, pressed):
    if pressed:
        record_event(EventType.MOUSE_PRESS, elapsed_time(), button, (x,y))
    else:
        record_event(EventType.MOUSE_RELEASE, elapsed_time(), button, (x,y))

def elapsed_time():
    global start_time
    return time() - start_time

def on_active():
    print('Global hotkey activated!')



def runListeners():
    #Collect mouse input events:
    global mouse_listener
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
    mouse_listener.wait()
    
    # Collect events until released in a non-blocking fashion:
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        global start_time
        start_time = time()
        listener.join()

    
if __name__ == "__main__":
    main()