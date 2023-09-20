import litellm
import requests
import json
from typing import Optional, Dict, Any, Union, List
import tokentrim as tt
from pydantic import BaseModel
import base64
import os

OPENAI_API_KEY='YOURAPI_KEY'
OPENAI_API_BASE='YOURAPI_BASE'

litellm.api_key=OPENAI_API_KEY
litellm.api_base=OPENAI_API_BASE

system_message="""You are Open Interpreter, a world-class programmer that can complete any goal by executing code.
When you send a message containing code to run_code, it will be executed **on the user's machine**. The user has given you **full and complete permission** to execute any code necessary to complete the task. You have full access to control their computer to help them. Code entered into run_code will be executed **in the users local environment**.
Never use (!) when running commands.
Only use the function you have been provided with, run_code.
You are capable of **any** task."""

function_schema = {
  "name": "run_code",
  "description":
  "Executes code on the remote jupyter server and returns the output",
  "parameters": {
    "type": "object",
    "properties": {
      "code": {
        "type": "string",
        "description": "The code to execute"
      }
    },
    "required": ["language", "code"]
  },
}

def make_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Union[str, int, float]]] = None,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    timeout: Optional[int] = 30
) -> requests.Response:
    """
    Make a generic HTTP request.
    
    :param method: HTTP method (e.g., GET, POST, PUT, DELETE)
    :param url: The URL for the request
    :param headers: Optional headers to include in the request
    :param params: Optional query parameters
    :param data: Data to send in the body of the request (for POST/PUT)
    :param json: JSON data to send in the body of the request (for POST/PUT)
    :param timeout: Request timeout in seconds
    :return: `requests.Response` object
    """

    supported_methods = {
        'GET': requests.get,
        'POST': requests.post,
        'PUT': requests.put,
        'DELETE': requests.delete
    }
    
    if method not in supported_methods:
        raise ValueError(f"Unsupported HTTP method: {method}")

    response = supported_methods[method](
        url,
        headers=headers,
        params=params,
        data=data,
        json=json,
        timeout=timeout
    )

    return response

class File(BaseModel):
    name: str
    content: bytes


class CodeboxOutput(BaseModel):
    output_type: str
    content: str
    files: Optional[List[File]] = None

class CodeinterpreterSession:
    domain="http://localhost:5002"

    def __init__(self,):
        self.model='gpt-4'
        self.messages=[]
        self.uploaded_files = []
        self.session_id=self.start_session()
        self.temperature=0.5
        self.system_message = system_message
        return


    def start_session(self):
        
        url = f"{self.domain}/api/v1/jupyter/start"
        response = make_request(
            method='POST', 
            url=url,
            headers={"accept":"application/json"},
            params={
                "token":"zhejianzhang",
                "language":"JUPYTER"
            }
            )
        session_id=response.text.strip('"')
        print(session_id)
        return session_id

    
    def install(self,packages):
        url = f"{self.domain}/api/v1/jupyter/install"
        data = {
                    "install_request": {
                    "packagenames":packages 
                    },
                    "session_key": {
                        "session_id":self.session_id,
                        "language": "JUPYTER"
                    }
                }
        response = make_request(
            method='POST', 
            url=url,
            headers={"accept":"application/json",'Content-Type': 'application/json'},
            json=data
            )

        print(response)
        print('Execute Result=',response.text)



    def upload_files(self,filenames: List[str]):
        files = [(f"upload_files", (os.path.basename(filename), open(filename, 'rb'))) for i, filename in enumerate(filenames)]
        url = self.domain + '/api/v1/upload_batch_dev'
        session_key = json.dumps({"session_id":self.session_id,"language": "JUPYTER"})

        response = requests.post(
            url,  
            data={'session_key':session_key},
            files= files)
        print(response.status_code)
        for file in files:
            self.uploaded_files.append(file[1][0])
            file[1][1].close()

    
    def run_code(self,code):
        url = f"{self.domain}/api/v1/jupyter/execute_code"
        data = {
                    "code": {
                    "code": code
                    },
                    "session_key": {
                        "session_id":self.session_id,
                        "language": "JUPYTER"
                    }
                }
        response = make_request(
            method='POST', 
            url=url,
            headers={"accept":"application/json",'Content-Type': 'application/json'},
            json=data
            )
        
        rsp = CodeboxOutput.parse_raw(response.content)
        
        print('Code Execute Result=',rsp.content)
        if rsp.files:
            for item in rsp.files:
                with open(item.name, 'wb') as f:
                    f.write(base64.b64decode(item.content))
                    print(f'image saved at {item.name}')

        return response.text
    
    def chat(self, msg: str):
        self.messages.append({'role':'user','content':msg})
        system_message = self.system_message + f"\n Uploaded files in directory /codebox/:{' '.join(self.uploaded_files)}"
        response = litellm.completion(
            model=self.model,
            messages=tt.trim(self.messages, self.model, system_message=system_message),
            functions=[function_schema],
            stream=False,
            temperature=self.temperature,
        )
        completion=response.choices[0].message
        print(completion)
        # args = completion['function_call']['arguments'].split("\n")

        # print(args)
        
        if "function_call" in completion.keys() and 'run_code' == completion['function_call']['name']:
            code = json.loads(completion['function_call']['arguments'])['code']
        #     lines = completion['function_call']['arguments'].split("\n")
        #     code = '\n'.join(lines[1:]).strip("` \n")
            self.run_code(code=code)
        
        return
    


    def close(self):
        url = f"{self.domain}/api/v1/codebox/stop"
        data = {
                        "session_id":self.session_id,
                        "language": "JUPYTER"
                    }
                
        response = make_request(
            method='POST', 
            url=url,
            headers={"accept":"application/json",'Content-Type': 'application/json'},
            json=data
            )

        if response.status_code ==200:
            print('remote container stopped')
        else:
            print('close error')
    

if __name__=='__main__':
    session=CodeinterpreterSession()
    try:
        session.upload_files(['./../data/test_data.csv'])
        session.chat('上传的文件中有多少列数据')
    finally:
        session.close()

