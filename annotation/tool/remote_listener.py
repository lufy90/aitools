
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import threading

class ThreadedRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

def start_rpc_server():
    server = ThreadedRPCServer(("0.0.0.0", 8000))
    server.register_function(lambda x, y: x + y, 'add')
    print("✅ RPC Server running on port 8000...")
    server.serve_forever()
