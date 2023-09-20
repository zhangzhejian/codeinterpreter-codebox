import subprocess
from fastapi import HTTPException
from collections import OrderedDict
from typing import List, Optional
from queue import Queue
import models.api as models
from models.api import File
import configs
import os
import errno
import docker
from docker.types import Mount
import base64
import models.schemas as schemas
import zipfile
import re
import socket, time, json, asyncio
from concurrent.futures import ThreadPoolExecutor
from jupyter_api import JupyterAPI

executor = ThreadPoolExecutor()
PROJECT_NETWORK='app_network_for_codebox'

def get_network_gateway_ip():
    client=docker.from_env()
    network=client.networks.get(PROJECT_NETWORK)
    gateway=network.attrs['IPAM']['Config'][0]['Gateway']
    print('network_gateway=', gateway)
    return gateway

PROJECT_NETWORK_GATEWAY=get_network_gateway_ip()



class LRUCacheCodebox:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: models.CodeboxSessionKey) -> "CodeboxSession":
        if key not in self.cache:
            return None
        value = self.cache.pop(key)
        # 把 key 放到最右边（也就是最新）
        self.cache[key] = value
        return value
    
    def remove(self, key:models.CodeboxSessionKey):
        if key in self.cache:
            self.cache.pop(key)

    async def put(self, key: models.CodeboxSessionKey, value: "CodeboxSession") -> None:
        if key in self.cache:
            # 如果 key 已经在 cache 中，先移除旧的
            self.cache.pop(key)
        elif len(self.cache) == self.capacity:
            # 如果 cache 已满，移除最左边的元素（也就是最老的）
            key,value=self.cache.popitem(last=False)
            value.stop()
        # 添加新的 key-value 到最右边（也就是最新）
        self.cache[key] = value

    def keys(self)->List[models.CodeboxSessionKey]:
        return self.cache.keys()



class GlobalCodeboxSessionManager(object):
    def __init__(self,):
        self.sessions= LRUCacheCodebox(10) 
    
    async def get_codebox_session(
            self, session_key:models.CodeboxSessionKey, 
            language:Optional[schemas.ProgrammingLanguage]=schemas.ProgrammingLanguage.JUPYTER
        )->"CodeboxSession":
        session=self.sessions.get(session_key)
        if session is None:
            session=CodeboxSession(
                session_id=session_key.session_id,
                language=language,
                )
            await self.sessions.put(key=session_key,value=session)
            return session
        else:
            return session
    
    def remove_session(self,session_key:models.CodeboxSessionKey):
        self.sessions.remove(session_key)

    
global_codebox_session_manager=GlobalCodeboxSessionManager()
PORT_RANGE=range(10000,40000)
PORTS_POOL = {}

def get_one_port():
    for port in PORT_RANGE:
        if port not in PORTS_POOL.keys():
            return port

class CodeboxSession:
    client_socket=None
    def __init__(self,session_id: str, language: schemas.ProgrammingLanguage):
        
        self.session_id = session_id
        self.language = language
        self.language_map=self._init_language_map()
        self.init_codebox_directory(self.session_id)
        self.container= self._create_container(language=self.language)
        self.network_gateway_ip=self._get_network_gateway_ip()
        
        # Start the container
        if self.language in [schemas.ProgrammingLanguage.JUPYTER]:
            self.container.start()
            self.container_ip_address = self._container_ip_address()
            print('_container_ip_address', self.container_ip_address)
            time.sleep(1)
            self.token = 'zhejianzhang'
            self.jupyter_api = JupyterAPI(port=self.export_port,ip=self.network_gateway_ip, token=self.token)

    def _init_language_map(self):
        return {
            schemas.ProgrammingLanguage.JUPYTER:{
                "image_name":"jupyter/scipy-notebook:custom", #You can modify the image
                # "command":'start-notebook.sh --NotebookApp.token="zhejianzhang" --ip="0.0.0.0" --no-browser --allow-root --allow_origin="*" --ServerApp.allow_remote_access=True --certfile=mycert.pem --keyfile=mykey.key',
                "command":'start-notebook.sh --NotebookApp.token="zhejianzhang" --ip="0.0.0.0" --no-browser --allow-root --allow_origin="*" --ServerApp.allow_remote_access=True ',
                "file_extension":".ipynb",
                "export_port":8888
            },
        }
    
    # def _jupyter_token(self):
    #     logs = self.container.logs().decode('utf-8')
    #     print(logs)
    #     token_pattern = r"token=([a-z0-9]+)"
    #     match = re.search(token_pattern, logs)
    #     if not match:
    #         raise ValueError("Token not found in container logs.")
    #     token = match.group(1)    
    #     return token
    

    def _get_network_gateway_ip(self):
        client=docker.from_env()
        network=client.networks.get(PROJECT_NETWORK)
        gateway=network.attrs['IPAM']['Config'][0]['Gateway']
        print('network_gateway=', gateway)
        return gateway


    def _create_container(self,language:schemas.ProgrammingLanguage):
        print("__init__ codeboxsession",self.root_path)
        client = docker.DockerClient(base_url='unix://var/run/docker.sock', timeout=20)
        mounts = [
            Mount(target="/codebox", source=f"{configs.codebox_root_path}{self.session_id}", type="bind"),
            Mount(target="/logs", source=f"{configs.codebox_root_path}{self.session_id}{configs.log_file_path}", type="bind")
        ]
        self.container_export_port = self.language_map[language]['export_port']
        self.export_port=get_one_port()
        PORTS_POOL[self.export_port] = schemas.PortOccupation(
            session_id=self.session_id,
            usage=schemas.PortUsage.EXPORT
        )
        port_mapping={
            '8888/tcp':self.export_port,
        }

        container = client.containers.create(self.language_map[language]['image_name'], 
                                     mounts=mounts,
                                     command=self.language_map[language]['command'],
                                     network_mode=PROJECT_NETWORK,
                                     ports = port_mapping, 
                                     detach=True)
        
        return container
    
    def _container_ip_address(self):
        client = docker.from_env()
        container = client.containers.get(self.container.name)
        return container.attrs['NetworkSettings']['Networks']['app_network_for_codebox']['IPAddress']
    
    def _form_image_name(self):
        return self.language_map[self.language]['image_name'] + self.session_id
        
    async def install_packages(self, packages:List[str])->tuple[list[str], list[str]]:
        code = f"!pip install {' '.join(packages)}"
        return self.jupyter_api.execute_code(code)

    
    async def arun_shell(self, command):
        loop = asyncio.get_event_loop()
        client = docker.from_env()
        exec_instance = await loop.run_in_executor(executor, client.api.exec_create, self.container.id, command, True, True, False)
        result = await loop.run_in_executor(executor, client.api.exec_start, exec_instance['Id'])
        print('exec_shell result:', result.decode('utf-8'))
        return result.decode('utf-8')


    def init_codebox_directory(self,session_id: str):
        self.root_path = f"/codebox/{session_id}"
        self.input_code_path = f"{self.root_path}{configs.input_code_path}"
        # self.upload_file_path= f"{self.root_path}{configs.upload_file_path}"
        # self.output_file_path= f"{self.root_path}{configs.output_file_path}"
        self.log_file_path= f"{self.root_path}{configs.log_file_path}"

        all_dirs = [
            self.root_path,
            self.input_code_path, 
            # self.upload_file_path,
            # self.output_file_path,
            self.log_file_path
        ]

        for item in all_dirs:
            if not os.path.exists(item):
                print(item)
                os.makedirs(item)
    
    def upload(self, file: File)-> tuple[bool, str]:
        file_path = f"{self.root_path}/{file.name}"
        try:
            with open(file_path, "wb") as f:
                f.write(file.content)
            if file.name.lower().endswith('.zip'):
                # 解压ZIP文件
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(file_path[:-4])
                    return (True, f'zip file {file.name} is extracted to {file_path}')
                except zipfile.BadZipFile:
                    os.remove(file_path)  # 删除不完整或损坏的ZIP文件
                    # raise HTTPException(status_code=400, detail="Invalid ZIP file")
                    return (False, f"{file.name} seems to be an invalid ZIP file")
        except OSError as e:
            if e.errno == errno.ENOSPC:
                raise HTTPException(status_code=400, detail="Insufficient disk space")
            else:
                raise
        return (True, "")
    
    def upload_batch(self, files: List[File]):
        for file in files:
            success = self.upload(file)
            print(file.name, success)

    
    #download from mnt
    def download(self, filename: str) -> File:
        if os.path.exists(filename):
            raise HTTPException(status_code=401, detail="File already exists")
        try:
            with open(filename) as f:
                file = File(
                    name=filename,
                    content=f.read()
                )
                return file
        except Exception as e:
            return None
        
    #download from jupyter
    def download_from_jupyter(self, filename):
        self.jupyter_api.download_file(filename)

    def before_execute(self,):
        if os.path.exists(f"{self.root_path}execute_lock"):
            os.remove(f"{self.root_path}execute_lock")
        with open(f"{self.root_path}execute_lock", 'w'):
            pass
        


    def execute_code(self, code: str):
        return self.jupyter_api.execute_code(code)




    def stop(self):
        try:
            if self.container:
                self.container.stop()
                self.container.remove()
        except Exception as e:
            print(e)

    
    def __del__(self):
        self.stop()
        return
    
        
        

        