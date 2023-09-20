# Codeinterpreter-codebox

这是Codeinterpreter-codebox,作为执行code interpreter代码的云服务。<br>


# Features
1. 独立的jupyter沙盒环境  
完全隔离的jupyter沙盒环境,支持状态保持的执行代码。支持文件上传、下载。
2. docker化一键部署<br>

3. 完全免费开源<br>
4. 信息安全<br>
支持完全私有化部署，无需上传文件到外部服务器<br>
5. 更灵活 <br>
支持开放更多端口以实现更多自定义功能需求，如：连接数据库、连接互联网、连接其他服务器

## 功能描述
1. 执行python代码
2. 支持上传文件的读取([上传文件并分析](./examples/client/codeinterpreter_session.py))  
```
if __name__=='__main__':
    session=CodeinterpreterSession()
    try:
        session.upload_files(['./../data/test_data.csv'])
        session.chat('上传的文件中有多少列数据')
    finally:
        session.close()
```
3. 支持下载沙盒中的文件
4. 支持动态扩容的商业化部署
5. 支持自定义功能修改，开放端口、网络连接等，支持爬虫。

## 相关项目和差异
1. [Code Interpreter api](https://github.com/shroominic/codeinterpreter-api)
2. [open-interpreter](https://github.com/KillianLucas/open-interpreter) 
3. [E2B](https://github.com/e2b-dev/e2b) 


| 特点/项目 | [Codeinterpreter-Codebox](https://github.com/zhangzhejian/codeinterpreter-codebox) | [Code Interpreter api](https://github.com/shroominic/codeinterpreter-api) | [open-interpreter](https://github.com/KillianLucas/open-interpreter) | [E2B](https://github.com/e2b-dev/e2b) |
|---|---|---|---|---|
| **私有商业化部署** | ✅ | ❌ | ❌| ❌ |
| **远程调用** | ✅ |✅ | ❌ | ✅ |
| **完全开源** | ✅ | ❌ | ✅ | ❌ |
| **免费** | ✅ | ❌ | ✅ | ❌ |
| **自定义修改** | ✅ | ❌ | ❌| ❌ |
| **信息安全** | ✅ | ❌ | ✅ | ❌ |
| **多编程语言支持** | ❌ | ❌ | ✅ | ✅ |
| **支持本地化运行** | ✅ | ✅ | ✅ | ❌ |
| **无需部署直接调用** | ❌ | ✅ | ✅ | ✅ |



## 代码示例

1. [jupyter server communicate](./examples/jupyter/jupyter_api_test.ipynb) 中展示了server和jupyter container交互的细节 
2. [jupyter 调用](./examples/jupyter/execute_dynamic_code.ipynb)中展示了如何通过http request的方式调用web服务，执行代码获取结果 
```
test_code="""
import docker
print(docker.__version__)

"""
execute(test_code)


#output
Execute Result= {"output_type":"text/plain","content":"6.1.3\n","files":null}
```
3. [client session调用](./examples/client/codeinterpreter_session.py)中展示了在项目中如何以session和http request的方式让LLM调用执行代码。  
```
session=CodeinterpreterSession()
try:
    session.upload_files(['./../data/test_data.csv'])
    session.chat('上传的文件中有多少列数据')
finally:
    session.close()
```

## 部署
[docker compose](./app/docker_dev.yml)中使用自己的文件路径替代'CODEBOX_ROOT_PATH'和 'YOUR_MNT_PATH:/codebox' 中的'YOUR_MNT_PATH'来挂载自己的文件路径


## 联系方式
微信:zjajzzj1996  
Email: [zhangzhehian@gmail.com](zhangzhehian@gmail.com)
