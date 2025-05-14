
import cv2
import numpy as np

def locate_svg(svg_path, screenshot, confidence=0.8):
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    icon = cv2.imread(svg_path, cv2.IMREAD_GRAYSCALE)

    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(gray_screenshot, icon, cv2.TM_CCOEFF_NORMED)

    loc = np.where(result >= confidence)
    if loc[0].size > 0:
        print('found at ()')
        return loc[1][0],loc[0][0]
    else:
        print('Not found')
        return None



if __name__ == '__main__':
    import pyautogui
    import sys
    svg_path = sys.argv[1]
    locate_svg(svg_path, pyautogui.screenshot())
