
from xmlrpc.server import SimpleXMLRPCServer
import pyautogui
import inspect
import pickle

from listener import on_event

pyautogui.PAUSE = 2

def get_func_names():
    return [f for f in dir(pyautogui) if inspect.isfunction(getattr(pyautogui, f))]

def set_attr(**kw):
    for k,v in kw.items():
        pyautogui[k] = v

def run_func(name):
    func = getattr(pyautogui, name)
    def runfunc(a, kw):
        try:
            ret = func(*a, **kw)
            return {"status":"success", "data":pickle.dumps(ret)}
        except Exception as e:
            return {"status":"fail", "data":str(e)}
    return runfunc

def listen(dev_name, event_name, timeout):
    try:
        event = on_event(dev_name, event_name, timeout=timeout)
        return {"status":"success", "data": pickle.dumps(event)}
    except Exception as e:
        return {"status":"fail", "data": str(e)}

def ping():
    return {"status": "success", "data": {}}

def run_server(host='0.0.0.0', port=8006):
    server = SimpleXMLRPCServer((host, port))
    for name in get_func_names():
        server.register_function(run_func(name), name)
    server.register_function(set_attr, 'set_attr')
    server.register_function(listen, 'listen')
    server.register_function(ping, 'ping')
    server.serve_forever()


if __name__ == '__main__':
    run_server()

