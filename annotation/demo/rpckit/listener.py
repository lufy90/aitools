
from enum import Enum
import pynput
import time

class Event():

    def __init__(self, name, **kwargs):
        self.name = name
        for k,v in kwargs.items():
            setattr(self, k, v)


def on_event(dev, name, timeout=300):
    if dev not in ['mouse','key']:
        raise ValueError(f"Invalid device: {dev}")

    if name not in ['press','release','move','click','scroll']:
        raise ValueError(f"Invalid event name: {name}")

    event = None
    x0, y0 = 0, 0


    def on_click(x, y, button, pressed):
        if name != "click":
            return

        if pressed:
            nonlocal x0, y0
            x0, y0 = x, y
        else:
            x1, y1 = x, y
            nonlocal event
            event = Event('click', start=(x0, y0), end=(x1, y1), button=button.name)

    def on_move(x, y):
        if name != "move":
            return
        nonlocal event
        event = Event('move', pos=(x,y))

    def on_scroll(x, y, dx, dy):
        if name != "scroll":
            return
        nonlocal event
        event =Event('scroll', pos=(x,y), offset=(dx,dy))

    def on_press(key):
        if name != "press":
            return
        try:
            kname = key.name
        except AttributeError:
            kname = key.char
        nonlocal event
        event = Event('press', kname=kname)

    def on_release(key):
        if name != "release":
            return
        try:
            kname = key.name
        except AttributeError:
            kname = key.char
        nonlocal event
        event = Event('release', kname=kname)


    event_handler_map = {
            'mouse': {
                'on_move': on_move,
                'on_click': on_click,
                'on_scroll': on_scroll,
                },
            'key': {
                'on_press': on_press,
                'on_release': on_release,
                }
            }
    listener = getattr(pynput, dev).Listener(
            **event_handler_map.get(dev)
            )
    listener.start()

    while timeout>0:
        if not event:
            time.sleep(1)
            timeout = timeout - 1
        else:
            return event

    raise TimeoutError(f'timeout on listening {dev} on {name}')

