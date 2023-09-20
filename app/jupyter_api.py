import requests
import time
import re
import json
from websocket import create_connection
import uuid
import datetime
import traceback
from models.api import File
import base64


def strip_ansi_escape_codes(s):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', s)


class JupyterAPI:

    def __init__(self, port, ip, token):
        self.NOTEBOOK_PATH = "main.ipynb"
        self.ip = ip
        self.token=token
        self.BASE_URL = f"http://{ip}:{port}/api/"
        self.WS_BASE_URL = f"ws://{ip}:{port}/api/"
        self.HEADERS = {
            "Authorization": f"token {token}"
        }
        self.session=self.create_session()
        self.kernel = self.session["kernel"]
        self.kernel_id = self.kernel["id"]
        self.ws = self.create_ws_conn()
    

    def create_session(self):
        url = self.BASE_URL + 'sessions'
        params = '{"path":\"%s\","type":"notebook","name":"","kernel":{"id":null,"name":"python3"}}' % self.NOTEBOOK_PATH
        response = requests.post(url, headers=self.HEADERS , data=params)
        session = json.loads(response.text)
        return session
    
    def create_ws_conn(self):
        ws = create_connection(f"{self.WS_BASE_URL}kernels/{self.kernel_id}/channels?session_id{self.session['id']}", header=self.HEADERS)
        return ws

    # def create_notebook(self):
    #     # 创建一个新的notebook
    #     r = requests.post(self.BASE_URL + "contents", headers=self.HEADERS, json={
    #         "type": "notebook",
    #         "path": "test_notebook.ipynb"
    #     }, timeout=10, verify=False)
    #     print(r.status_code)
    #     print(r.content)
    #     notebook_path = r.json()["path"]

    # def create_kernel(self):
    #     # 创建一个新的kernel
    #     r = requests.post(self.BASE_URL + "kernels", headers=self.HEADERS,timeout=5,verify=False)
    #     kernel_id = r.json()["id"]
    #     return kernel_id
    
    def send_execute_request(self,code, msg_id):
        msg_type = 'execute_request'
        content = { 'code' : code, 'silent':False }
        hdr = { 'msg_id' :msg_id, 
            'username': 'codebox', 
            'session': self.session['id'], 
            'data': datetime.datetime.now().isoformat(),
            'msg_type': msg_type,
            'version' : '5.0' }
        msg = { 'header': hdr, 'parent_header': hdr, 
            'metadata': {},
            'content': content }
        return msg
    
    def download_file(self, filename):
        file_url = f"http://{self.ip}:{self.port}/files/{filename}?token={self.token}"
        response = requests.get(file_url)
        with open(filename, "wb") as f:
            f.write(response.content)

    def execute_code(self, code: str)->tuple[list[str], list[str]]:
        msg_id=  uuid.uuid1().hex
        msg = self.send_execute_request(code, msg_id)
        self.ws.send(json.dumps(msg))
        try:
            img_index=0
            msg_type = ''
            stdoutputs = []
            image_datas = []
            while True:
                rsp = json.loads(self.ws.recv())
                msg_type = rsp["msg_type"]
                # print(msg_type)
                if msg_type == "status" and rsp["content"]["execution_state"] == "idle" and rsp["parent_header"]['msg_id']==msg_id:
                    print('execute end')
                    break
                if msg_type == "stream":
                    stdoutput=rsp["content"]["text"]
                    if isinstance(stdoutput,list):
                        stdoutput=[strip_ansi_escape_codes(item) for item in stdoutput]
                        stdoutputs+=stdoutput
                    else:
                        stdoutputs.append(stdoutput)
                elif msg_type == "execute_result":
                    if "image/png" in (rsp["content"]["data"].keys()):
                        image_data = rsp["content"]["data"]["image/png"]
                        image_datas.append(File(name=f"{msg_id}_{img_index}.png", content=image_data))
                        img_index+=1
                    else:
                        stdoutput=rsp["content"]["data"]["text/plain"]
                        if isinstance(stdoutput,list):
                            stdoutputs+=stdoutput
                        else:
                            stdoutputs.append(stdoutput)
                elif msg_type == "display_data":
                    image_data = rsp["content"]["data"]["image/png"]
                    image_datas.append(File(name=f"{msg_id}_{img_index}.png", content=image_data))
                    img_index+=1
                elif msg_type == "error":
                    error_output=rsp["content"]["traceback"]
                    if isinstance(error_output,list):
                        error_output=[strip_ansi_escape_codes(item) for item in error_output]
                        stdoutputs+= error_output
                    else:
                        cleaned_string = strip_ansi_escape_codes(error_output)
                        stdoutputs.append(cleaned_string)
                else:
                    pass
        except:
                traceback.print_exc()
                return (stdoutputs, image_datas)
        
        return (stdoutputs, image_datas)

    

    def __del__(self):
        if self.ws:
            print('ws closed')
            self.ws.close()
        # 清理资源
        # requests.delete(self.BASE_URL + f"kernels/{kernel_id}", headers=HEADERS)
        # requests.delete(self.BASE_URL + f"contents/{notebook_path}", headers=HEADERS)
        pass
if __name__=='__main__':
    print('start')
    api = JupyterAPI(port=10001, ip='localhost', token='zhejianzhang')
    api.create_notebook()