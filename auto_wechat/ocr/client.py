
import sys
import pickle
import base64

import xmlrpc.client
import numpy as np


def get_text(img_b64, url="http://10.7.13.40:10002"):
    proxy = xmlrpc.client.ServerProxy(url)
    ret = proxy.get_text(img_b64)
    data = base64.b64decode(ret)
    return pickle.loads(data)


if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    print(get_text(img_b64))
