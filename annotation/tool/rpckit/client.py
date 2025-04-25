import pickle
import xmlrpc.client

class Client():
    def __init__(self, server):
        self.proxy = xmlrpc.client.ServerProxy(server)

    def run(self, func, *a, **kw):
        ret = getattr(self.proxy, func)(a,kw)
        if ret['status'] == 'success':
            return pickle.loads(ret['data'].data)
        else:
            raise Exception('rpc failed: ' + ret['data'])

    def listen(self, dev_name, event_name, timeout):
        # listen keyboard and mouse event, return event data
        ret = self.proxy.listen(dev_name, event_name, timeout)
        print('ret:', ret)

        if ret['status'] != 'success':
            raise Exception(f"listen {event_name} failed: {ret['data']}")
        else:
            return pickle.loads(ret['data'].data)
