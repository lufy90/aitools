
import pyautogui
from pynput.keyboard import Controller, Key
import pyperclip
from pypinyin import lazy_pinyin

import os
import sys
import logging
import time
from pydantic import BaseModel
from io import BytesIO
import base64
import re
import subprocess
import json

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

def get_card_bottom_y():
     bottom_icon_box = get_icon_position('card_bottom')
     return bottom_icon_box.top + int(bottom_icon_box.height) + 20

def get_dept_position():
    dept_text_box = get_icon_position('dept_text')
    return (dept_text_box.left + 100, dept_text_box.top + 10)

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
    window = subprocess.check_output("DISPLAY=:0 xdotool search --name 企业微信 | tail -n 1", shell=True, text=True)
    #window = subprocess.check_output("DISPLAY=:0 xdotool search --name 企业微信 getwindowpid | tail -n 1", shell=True, text=True)
    window = window.strip()
    #window = 136314888
    print(f'wechat window: {window}')
    os.system(f'xdotool windowactivate {window}')
    time.sleep(2)

    img_b64 = get_card(name)
    text_total = ""
    no = ""
    email = ""
    duty = ""
    dept = ""
    is_valid = True
    ocr_res = []

    if not img_b64:
        is_valid = False
    else:
        ocr_res = get_text(img_b64)

    for i in ocr_res:
        text = i.get('text')
        # skip water mark
        if text.startswith('@'):
            continue
        if text.startswith('UT'):
            no = text
        if text.endswith('.com'):
            email = text
        if text.endswith('总监') or text.endswith('经理') or text.endswith('专家') or text.endswith('师'):
            duty = text
        if '已离职' in text:
            is_valid = False
        text_total = text_total + text + "\n"
    print('text:', text_total)

    if is_valid:
        x,y = get_dept_position()
        pyautogui.rightClick(x,y)
        pyautogui.click(x+10,y+10)
        dept = pyperclip.paste()
        print(f'dept: {dept}')
    #pattern = f"部门(.*?)企业\n"
    #dept_strings = re.findall(pattern, text_total, re.DOTALL)
    #print('dept_strings:', dept_strings)
    #if len(dept_strings) >0:
    #    dept = dept_strings[0].replace('\n','')
    #    # replace number in dept name (in case of water mark number)
    #    dept = re.sub(r'\d+', '', dept)
    p_info = {
            'no': no,
            'duty': duty,
            'email': email,
            'dept': dept,
            'name': name,
            'is_valid': is_valid
            }
    with open(f'./samples/{name}.json', 'w') as f:
        json.dump(p_info, f)
    return WechatPerson(**p_info)


def get_card(name, debug=True):
    '''
    name: person name
    '''
    search_pos = get_search_input_position()
    print(f'position: {search_pos}')
    pyautogui.click(search_pos)
    pyautogui.press('backspace', presses=20, interval=0.1)
    #pyperclip.copy(name)
    #with keyboard.pressed(Key.ctrl if not 'darwin' in sys.platform else Key.cmd):
    #    keyboard.press('v')
    #    keyboard.release('v')
    k = Controller()
    #k.type(name)
    name_pinyin = lazy_pinyin(name)
    logging.info(f"search input: {name_pinyin}")
    for i in list(name_pinyin):
        for j in i:
            k.press(j)
            k.release(j)
            time.sleep(0.2)
        #k.type(i)
        #print(f'input: {i}')
        #k = Controller()
        #k.press(i)
        #k.release(i)
        time.sleep(0.5)
    #for i in get_info_positions():
    try:
        x,y = get_info_positions()
    except:
        logging.warning(f'user invalid: name')
        return None
    pyautogui.click(x,y)
    time.sleep(2)
    try:
        bottom_y = int(get_card_bottom_y() - y +31)
    except:
        bottom_y = 392
    card_region = (int(x+28), int(y-31), 320, bottom_y)
    logging.info(f'card_region: {card_region}')
    img = pyautogui.screenshot(region=card_region)
    if debug:
        count = 0
        fname = f'./samples/{name}_{count}.png'
        while True:
            if not os.path.isfile(fname):
                break
            count = count + 1
            fname = f'./samples/{name}_{count}.png'
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
    is_valid: bool = True


if __name__ == '__main__':
    #os.system('xdotool windowactivate 127926280')
    #time.sleep(2)
    print(get_person(sys.argv[1]))
