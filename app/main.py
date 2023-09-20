import uuid
from fastapi import FastAPI, Depends, HTTPException, UploadFile,File, Form
from pydantic import BaseModel
import docker
from docker.errors import NotFound
from starlette.requests import Request
from docker.types import Mount
import os
from typing import Optional, List
import configs
from codebox_session import global_codebox_session_manager
import models.api as models
import models.schemas as schemas
import asyncio


app = FastAPI()
def validate_token(token:str):
    return token in configs.allowed_tokens


@app.post("/api/v1/jupyter/start")
async def start_codebox(token: str, language:schemas.ProgrammingLanguage) -> str:
    valid = validate_token(token)
    if not valid:
        return None
    session_id = str(uuid.uuid4())
    await global_codebox_session_manager.get_codebox_session(
        session_key=models.CodeboxSessionKey(session_id=session_id, language=language), 
        language=language)
    return session_id

@app.post("/api/v1/jupyter/execute_code", response_model=Optional[models.CodeboxOutput])
async def execute_code(code: models.Code,  session_key:models.CodeboxSessionKey) -> models.CodeboxOutput:
    if session_key not in global_codebox_session_manager.sessions.keys():
        raise HTTPException(400, detail=f"{session_key.session_id} not started")
    session = await global_codebox_session_manager.get_codebox_session(session_key=session_key)
    result = session.execute_code(code=code.code)
    print(result)
    return models.CodeboxOutput(
        output_type="text/plain" if len(result[1])<=0 else 'files/mixed',
        content='\n'.join(result[0]),
        files = result[1] if len(result[1])>0 else None
    )

@app.post("/api/v1/jupyter/install", response_model=str)
async def install(install_request:models.CodeboxInstallRequest,session_key:models.CodeboxSessionKey):
    if session_key not in global_codebox_session_manager.sessions.keys():
        raise HTTPException(400, detail=f"{session_key.session_id} not started")
    session = await global_codebox_session_manager.get_codebox_session(session_key=session_key)
    await session.install_packages(install_request.packagenames)
    return 'installed'


@app.post("/api/v1/execute_shell", response_model=Optional[models.CodeboxOutput])
async def execute_code(code: models.Code,  session_key:models.CodeboxSessionKey) -> models.CodeboxOutput:
    if session_key not in global_codebox_session_manager.sessions.keys():
        raise HTTPException(400, detail=f"{session_key.session_id} not started")
    session = await global_codebox_session_manager.get_codebox_session(session_key=session_key)
    try:
        execute_result = await asyncio.wait_for(session.arun_shell(code.code), timeout=20)
    except asyncio.TimeoutError as e:
        execute_result=f"The Execution of command '{code.code}' seems take too long.Maybe you don't need to wait for the result, please specify need re-execute or not."
    return models.CodeboxOutput(
        content=execute_result,
        output_type='shell'
    )

@app.post("/api/v1/upload")
async def upload(file: models.File, session_key:models.CodeboxSessionKey):
    session = await global_codebox_session_manager.get_codebox_session(session_key)
    return session.upload(file)


@app.post("/api/v1/upload_dev")
async def upload(session_key:Optional[str]=Form(None),file: UploadFile=File(...)):
    print(session_key)
    try:
        session_key = models.CodeboxSessionKey.parse_raw(session_key)
    except Exception as e:
        print(e)
        return HTTPException(status_code=400, detail='bad request with wrong format of session_key')
    print(session_key)
    session = await global_codebox_session_manager.get_codebox_session(session_key)
    file = models.File(
        name=file.filename,
        content=await file.read(),
    )
    print(file.name)
    return session.upload(file)


@app.post("/api/v1/upload_batch_dev")
async def upload(session_key:Optional[str]=Form(None),upload_files: List[UploadFile]=File(...)):
    try:
        if session_key:
            session_key = models.CodeboxSessionKey.parse_raw(session_key)
    except Exception as e:
        print(e)
        return HTTPException(status_code=400, detail='bad request with wrong format of session_key')
    print('uploaded files:', upload_files)
    session = await global_codebox_session_manager.get_codebox_session(session_key)
    processed_files = [models.File(
        name=file.filename,
        content=await file.read(),
    ) for file in upload_files]
    return session.upload_batch(processed_files)

@app.post('/api/v1/jupyter/download')
async def download(session_key:models.CodeboxSessionKey,filenames: List[str]) -> List[models.File]:
    session = await global_codebox_session_manager.get_codebox_session(session_key)
    file_list:List[models.File] = []
    for filename in filenames:
        try:
            file_list.append(session.download(filename))
        except Exception as e:
            print(e)
    return file_list


    
@app.post("/api/v1/codebox/stop")
async def close_codebox(session_key:models.CodeboxSessionKey):
    session = await global_codebox_session_manager.get_codebox_session(session_key)
    session.stop()
    global_codebox_session_manager.remove_session(session_key)


@app.on_event('shutdown')
async def shutdown():
    print('on shutting down')
    session_keys = global_codebox_session_manager.sessions.keys()
    for item in list(session_keys):
        global_codebox_session_manager.remove_session(item)
    print('all containers closed')
