
from client import api


def gen_case(code_path, host, model):
    with open(code_path,'r') as f:
        code = f.read()
    prompt = f"""请为下面的内核代码生成kunit测试用例：```{code}```"""
#    prompt = f"""输出下面代码中的所有函数：```{code}```"""
    res = api(prompt, host=host, model=model)
    return res

if __name__ == '__main__':
    import sys
    host="http://10.10.16.11:11434"
    #model="deepseek-coder-v2"
    model="deepseek-r1:32b"
    res = gen_case(sys.argv[1], host, model)
    print(f'model: {res["model"]}')
    print(f'total_duration: {res["total_duration"]/1000/1000/1000}')
    print(f'response: {res["response"]}')
