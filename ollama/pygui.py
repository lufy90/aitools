
import importlib
import inspect
import pydoc

def get_available_methods(module_name:str):
    module = importlib.import_module(module_name)
    return [{"name":f, "doc":pydoc.getdoc(f)} for f in dir(module) if inspect.isfunction(getattr(module, f))]

if __name__ == '__main__':
    res = get_available_methods('pyautogui')
    print(res)
