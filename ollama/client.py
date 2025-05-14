
try:
    from ollama import Client
    use_ollama_client = True
except:
    import requests
    use_ollama_client = False

if not requests:
    import requests

def chat(host, model):
    while True:
        content = input("> ")
        if content == 'exit':
            break
        if len(content) == 0:
            continue
        if not content:
            continue
        if use_ollama_client:
            client = Client(host=host)
            res = client.chat(model='deepseek-r1:32b', messages=[
                {
                    "role":"user",
                    "content": content,
                    },
                ])
            print(res.message.content)
        else:
            url = f'{host}/api/generate'
            data = {
                    "model": model,
                    "prompt": content,
                    "stream": False,
                    }
            res = requests.post(url, json=data)
            if not res.ok:
                raise Exception('request failed:',res.status_code)
            res_data = res.json()
            print(res_data["response"])

def api(prompt, host="http://10.10.16.11:11434", model="deepseek-r1:32b"):
    url = f'{host}/api/generate'
    data = {
            "model":model,
            "prompt":prompt,
            "stream":False,
            }
    res = requests.post(url, json=data)
    if not res.ok:
        raise Exception('request failed due to: ', res.status_code)
    return res.json()

if __name__ == '__main__':
    import sys
    try:
        host = sys.argv[1]
        model = sys.argv[2]
    except:
        host = "http://10.10.16.11:11434"
#        model = "deepseek-r1:32b"
        model = "deepseek-coder-v2"
    chat(host, model)
