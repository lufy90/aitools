# UI operation toolkit

## Run server

```
# In bash
DISPLAY=:0 python server.py
```

## On client

### Make remote pyautogui call

```
# in python
from client import Client
c = Client('http://localhost:8006')
img = c.run('screenshot')
img.save('./screenshot.png')
```

### Listen remote keyboard or mouse event

```
event = c.listen('mouse','click',300)
print(event.start)
print(event.end)
print(event.button)
```
