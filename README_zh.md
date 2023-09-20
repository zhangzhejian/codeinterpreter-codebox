# Codeinterpreter-codebox

这是一个通过docker构建的云服务，实现了code interpreter的后端功能，以便部署调用。Sandbox环境语言独立，可以用其他编程语言重写。
实现了企业化的code interpreter代码执行的自我部署的实现，提供了更好的信息安全性和基于云的可拓展性和可用性。
## 相关项目和差异
1. [Code Interpreter api](https://github.com/shroominic/codeinterpreter-api)提供了基于langchain的agent调用，但是codebox为闭源收费。
2. [open-interpreter](https://github.com/KillianLucas/open-interpreter) 提供了更多的编程语言支持，但是支持本地化运行，不支持远程调用。在商业化或者企业化的项目中无法应用
3. [E2B](https://github.com/e2b-dev/e2b) 支持更多编程语言的云服务，闭源



## 功能描述
1. 通过支持启动、运行、上传文件、安装python package、结束等接口，方便客户端对于codeinterpreter-codebox的调用
2. 提供了docker化的虚拟环境作为代码执行的沙盒环境
3. 可以增加调用管理的数据库模块功能

## 部署
[docker compose](./app/docker_dev.yml)中使用自己的文件路径替代'CODEBOX_ROOT_PATH'和 'YOUR_MNT_PATH:/codebox' 中的'YOUR_MNT_PATH'来挂载自己的文件路径
## 代码示例

1. [jupyter server communicate](./examples/jupyter/jupyter_api_test.ipynb) 中展示了server和jupyter container交互的细节 
2. [jupyter 调用](./examples/jupyter/execute_dynamic_code.ipynb)中展示了如何通过http request的方式调用web服务，执行代码获取结果
3. [client session调用](./examples/client/codeinterpreter_session.py)中展示了在项目中如何以session和http request的方式让LLM调用执行代码。




## 联系方式
微信:zjajzzj1996
Email: [zhangzhehian@gmail.com](zhangzhehian@gmail.com)
