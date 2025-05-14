import os
import time
import requests
from sec import PRODUCTS

class Client:
    def __init__(self, product, model):
        self.product = PRODUCTS.get(product)
        self.product_name = product
        if not self.product:
            raise Exception('product not available')
        self.model = model
        self.headers = {"Content-Type":"application/json","Authorization":"Bearer "+self.product['key']}

    def chat(self, prompts, messages):
        if self.product_name == 'ollama':
            message = [
                    {
                        "role":"user", "content": f'{prompts}\n{messages}'
                    }
                    ]
        else:
            messages = [
                {"role": "system","content": prompts},
                {"role": "user", "content": messages}
                ]

        data = {
            "temperature":0.6,
            "model":self.model,
            "messages": messages
        }
        response = requests.post(self.product['url'], headers=self.headers, json=data, stream=False)
        return response

if __name__ == '__main__':
    from youqu.sys_prompts import sys_gen_script as sys_prompts
    with open('youqu/tcase_02.txt', 'r') as f:
        user_prompts = f.read()
    client = Client('doubao', 'deepseek-v3-241226')
    #client = Client('doubao', 'ep-20250123134020-fkp6p')
    #res = client.chat(sys_gen_script, "使用快捷键Ctrl+Alt+Delete可唤出关机界面,检查是否显示重启按钮")
    res = client.chat(sys_prompts, user_prompts)
    res_json = res.json()
    print(res_json.get("choices")[0].get("message").get("content"))
