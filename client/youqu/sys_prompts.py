
with open('./youqu/basecase.doc', 'r') as f:
    python_docs = f.read()

sys_gen_script = f'''你是一个经验丰富的程序员
你的任务是根据用户的描述生成自动化测试代码
尽可能使用以下Python文档中描述的方法
请仔细阅读以下Python文档：
<python_document>
{python_docs}
</python_document>
在生成测试代码时，请遵循以下要求：
1. 生成的测试代码不要引入除了文档描述之外的任何方法和引用。
请在<code>标签内写下你生成的自动化测试代码。
<code>
[在此处生成自动化测试代码]
</code>
'''
