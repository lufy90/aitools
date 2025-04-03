
from xmlrpc.server import SimpleXMLRPCServer
from cnocr import CnOcr
from PIL import Image

from io import BytesIO
import base64
import pickle

def get_text(b64):
    ocr = CnOcr()
    img_data = base64.b64decode(b64)
    img = Image.open(BytesIO(img_data))
    ret = ocr.ocr(img)
    data = pickle.dumps(ret)
    encoded_data = base64.b64encode(data).decode("utf-8")

    return encoded_data

def run_server(host='0.0.0.0', port=10002):
    server = SimpleXMLRPCServer((host, port))
    server.register_function(get_text, 'get_text')
    server.serve_forever()

if __name__ == '__main__':
    run_server()

