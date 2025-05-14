import asyncio
import json
import pyautogui
import base64
import io
import websockets
from PIL import Image
from pynput import mouse, keyboard

connected_clients = set()

async def handle_command(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                cmd = data.get("command")
                args = data.get("args", {})

                if cmd == "move":
                    pyautogui.moveTo(args["x"], args["y"])
                elif cmd == "click":
                    pyautogui.click()
                elif cmd == "type":
                    pyautogui.write(args.get("text", ""))
                elif cmd == "screenshot":
                    screenshot = pyautogui.screenshot()
                    buffer = io.BytesIO()
                    screenshot.save(buffer, format="PNG")
                    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
                    await websocket.send(json.dumps({
                        "type": "screenshot",
                        "data": encoded
                    }))
                else:
                    await websocket.send(json.dumps({"error": "Unknown command"}))
            except Exception as e:
                await websocket.send(json.dumps({"error": str(e)}))
    finally:
        connected_clients.remove(websocket)

async def send_event(event_data):
    if connected_clients:
        msg = json.dumps({**event_data})
        await asyncio.gather(*(client.send(msg) for client in connected_clients))

def start_pynput_listeners(loop):
    def on_move(x, y):
        asyncio.run_coroutine_threadsafe(
                send_event({"type": "move", "device":"mouse", "args": {"x": x, "y": y}}),
            loop
        )
    x0, y0 = 0, 0

    def on_click(x, y, button, pressed):
        nonlocal x0, y0
        if pressed:
            x0, y0 = x, y
        else:
            x1, y1 = x, y
            asyncio.run_coroutine_threadsafe(
                send_event({
                    "type": "click",
                    "device": "mouse",
                    "args": {
                        "x0": x0, "y0": y0,
                        "x1": x, "y1": y,
                        "button": button.name,
                        }
                }),
                loop
            )

    def on_scroll(x, y, dx, dy):
        asyncio.run_coroutine_threadsafe(
            send_event({
                "type": "scroll", "device": "mouse",
                "args":{
                    "x": x, "y": y, "dx": dx, "dy": dy
                    }
                }),
                loop
            )

    def on_press(key):
        asyncio.run_coroutine_threadsafe(
                send_event({"type": "press", "device":"keyboard", "args": {"key": str(key)}}),
            loop
        )

    mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll).start()
    keyboard.Listener(on_press=on_press).start()

async def main():
    loop = asyncio.get_running_loop()
    start_pynput_listeners(loop)
    async with websockets.serve(handle_command, "0.0.0.0", 6789):
        print("WebSocket server started on ws://0.0.0.0:6789")
        await asyncio.Future()
#    start_server = websockets.serve(handle_command, "0.0.0.0", 6789)
#    loop.run_until_complete(start_server)
#    print("WebSocket server started on ws://0.0.0.0:6789")
#    loop.run_forever()

if __name__ == "__main__":
    asyncio.run(main())

