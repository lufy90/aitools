
from client import Client

with open('prompt.md', 'r') as f:
    prompt = f.read()
client = Client('doubao','deepseek-v3-241226')
res = client.chat(prompt,'')
print(res.json())
