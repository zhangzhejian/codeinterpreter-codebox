# Codeinterpreter-Codebox

This is Codeinterpreter-codebox, a cloud service for executing Code Interpreter code.

# Features
1. 🐍 **Independent Jupyter Sandbox Environment**  
A completely isolated Jupyter sandbox environment that supports state-preserving code execution. Supports file uploads and downloads.
2. 🐳 **Dockerized One-click Deployment**  
3. 🌐 **Completely Free and Open Source**  
4. 🛡️ **Information Security**  
Supports completely private deployments without the need to upload files to external servers.
5. 🚀 **More Flexible**  
Supports the opening of more ports to achieve more custom functionality requirements, such as: connecting to databases, connecting to the internet, connecting to other servers.

## Function Descriptions
1. Execute Python code.
2. Supports reading of uploaded files ([Upload and Analyze Files](./examples/client/codeinterpreter_session.py)).  
```
if name=='main':
session=CodeinterpreterSession()
try:
session.upload_files(['./../data/test_data.csv'])
session.chat('How many columns are in the uploaded file?')
finally:
session.close()
```
3. Supports downloading files from the sandbox.
4. Supports dynamic scaling for commercial deployments.
5. Supports custom feature modifications, open ports, network connections, etc., supports web crawlers.

## Related Projects and Differences
1. [Code Interpreter api](https://github.com/shroominic/codeinterpreter-api)
2. [open-interpreter](https://github.com/KillianLucas/open-interpreter) 
3. [E2B](https://github.com/e2b-dev/e2b) 

| Feature/Project | [Codeinterpreter-Codebox](https://github.com/zhangzhejian/codeinterpreter-codebox) | [Code Interpreter api](https://github.com/shroominic/codeinterpreter-api) | [open-interpreter](https://github.com/KillianLucas/open-interpreter) | [E2B](https://github.com/e2b-dev/e2b) |
|---|---|---|---|---|
| **Private Commercial Deployment** | ✅ | ❌ | ❌| ❌ |
| **Remote Invocation** | ✅ |✅ | ❌ | ✅ |
| **Fully Open Source** | ✅ | ❌ | ✅ | ❌ |
| **Free of Charge** | ✅ | ❌ | ✅ | ❌ |
| **Custom Modifications** | ✅ | ❌ | ❌| ❌ |
| **Information Security** | ✅ | ❌ | ✅ | ❌ |
| **Supports Multiple Programming Languages** | ❌ | ❌ | ✅ | ✅ |
| **Supports Local Execution** | ✅ | ✅ | ✅ | ❌ |
| **Direct Invocation Without Deployment** | ❌ | ✅ | ✅ | ✅ |

## Code Examples
1. [jupyter server communicate](./examples/jupyter/jupyter_api_test.ipynb) showcases the details of interaction between the server and the Jupyter container.
2. [jupyter call](./examples/jupyter/execute_dynamic_code.ipynb) demonstrates how to invoke a web service via an HTTP request, execute code, and retrieve results. 
```
test_code="""
import docker
print(docker.version)

"""
execute(test_code)

#output
Execute Result= {"output_type":"text/plain","content":"6.1.3\n","files":null}
```
3. [client session invocation](./examples/client/codeinterpreter_session.py) shows how to allow LLM to invoke and execute code in a project through session and HTTP request.
```
session=CodeinterpreterSession()
try:
session.upload_files(['./../data/test_data.csv'])
session.chat('How many columns are in the uploaded file?')
finally:
session.close()
```


## Deployment
In [docker compose](./app/docker_dev.yml), replace 'CODEBOX_ROOT_PATH' and 'YOUR_MNT_PATH:/codebox' with your own file path for 'YOUR_MNT_PATH' to mount.

## Contact
WeChat: zjajzzj1996  
Email: [zhangzhehian@gmail.com](zhangzhehian@gmail.com)
