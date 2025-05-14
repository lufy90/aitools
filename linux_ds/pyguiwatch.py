
import pyautogui
import time

def watch_mouse_clicks():
    while True:
        if pyautogui.mouseDown(button='left'):
            print("Left mouse button down")
            while pyautogui.mouseDown(button='left'):
                time.sleep(0.1)
            print("Left mouse button up")
        elif pyautogui.mouseDown(button='right'):
            print("Right mouse button down")
            while pyautogui.mouseDown(button='right'):
                time.sleep(0.1)
            print("Right mouse button up")
        elif pyautogui.mouseDown(button='middle'):
            print("Middle mouse button down")
            while pyautogui.mouseDown(button='middle'):
                time.sleep(0.1)
            print("Middle mouse button up")
        time.sleep(0.1)

if __name__ == "__main__":
    watch_mouse_clicks()
