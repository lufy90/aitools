
import pyautogui
from pynput.keyboard import Controller
import os
import sys
import logging
import time
from pydantic import BaseModel
from io import BytesIO
import base64
import re

from ocr.client import get_text

PERSON_ITEM_HEIGHT = 64
PERSON_ITEM_WEIGHT = 400


pyautogui.PAUSE = 1

logging.basicConfig(level=logging.DEBUG)

def get_icon_position(name):
    logging.debug(f'locate {name}.png')
    try:
        pos = pyautogui.locateOnScreen(f'./icons/{name}.png')
        logging.info(f'position of {name} is {pos}')
        return pos
    except Exception as e:
        return None

def get_search_input_position():
    search_icon_box = get_icon_position('search')
    logging.info(f'search_icon_box: {search_icon_box}')
    offset = 30
    return (search_icon_box.left + search_icon_box.left + offset, 
            search_icon_box.top + int(search_icon_box.height /2)
            )

def get_count():
    top_position = get_icon_position('contact')
    bottom_position = get_icon_position('in_chat_group')
    person_items_height = bottom_position.top - top_position.top
    return int(person_items_height / PERSON_ITEM_HEIGHT)

def get_info_positions():
    top_position = get_icon_position('info_icon')
    if not top_position:
        raise Exception('No such person')
    bottom_position = get_icon_position('bottom')

    x, y = (
            top_position.left + int(top_position.width / 2), 
            top_position.top + int(top_position.height / 2)
            )
    positions = [(x,y),]
    #while  y + PERSON_ITEM_HEIGHT < bottom_position.top:
    #    positions.append((x,y + PERSON_ITEM_HEIGHT))
    #    y = y + PERSON_ITEM_HEIGHT

    return x, y

def get_person(name: str):
    img_b64 = get_card(name)
    ocr_res = get_text(img_b64)
    text_total = ""
    for i in ocr_res:
        text = i.get('text')
        # skip water mark
        if text.startswith('@'):
            continue
        if text.startswith('UT'):
            no = text
        if text.endswith('.com'):
            email = text
        if text.endswith('工程师') or text.endswith('总监'):
            duty = text
        text_total = text_total + text + "\n"
    print('text:', text_total)
    pattern = f"部门(.*?)企业"
    dept_strings = re.findall(pattern, text_total, re.DOTALL)
    print('dept_strings:', dept_strings)
    dept = dept_strings[0].replace('\n','')
    # replace number in dept name (in case of water mark number)
    dept = re.sub(r'\d+', '', dept)
    return WechatPerson(no=no, email=email, dept=dept,duty=duty, name=name)


def get_card(name, debug=False):
    '''
    name: person name
    '''
    search_pos = get_search_input_position()
    print(f'position: {search_pos}')
    pyautogui.click(search_pos)
    pyautogui.press('backspace', presses=20, interval=0.1)
    logging.info(f"search input: {name}")
    for i in list(name):
        k = Controller()
        k.press(i)
        k.release(i)
        time.sleep(2)
    time.sleep(2)
    #for i in get_info_positions():
    x,y = get_info_positions()
    pyautogui.click(x,y)
    time.sleep(2)
    card_region = (int(x+28), int(y-31), 320, 392)
    logging.info(f'card_region: {card_region}')
    img = pyautogui.screenshot(region=card_region)
    if debug:
        count = 0
        fname = f'./cards/{name}_{count}.png'
        while True:
            if not os.path.isfile(fname):
                break
            count = count + 1
            fname = f'./cards/{name}_{count}.png'
        img.save(fname)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

class WechatPerson(BaseModel):
    no: str = ""
    name: str = ""
    email: str = ""
    dept: str = ""
    duty: str = ""


if __name__ == '__main__':
    os.system('xdotool windowactivate 127926280')
    time.sleep(2)
    print(get_person(sys.argv[1]))
