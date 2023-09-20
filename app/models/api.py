from pydantic import BaseModel, validator
from typing import List, Optional
import json
import datetime
from models.schemas import ProgrammingLanguage


class Code(BaseModel):
    code: str


class CodeModification(BaseModel):
    origin_code: str
    new_code: str
    filepath: str

    def on_duplicate(self):
        return f"Duplicate target code to replace found in {self.filepath}: {self.origin_code}"
    
    def on_not_found(self):
        return f"{self.origin_code} not found in {self.filepath}"

class CodeboxInitRequest(BaseModel):
    token: str

class CodeboxSessionKey(BaseModel):
    session_id: str
    language: ProgrammingLanguage
    def __hash__(self):
        return hash(self.session_id)

    def __eq__(self, other):
        if isinstance(other, CodeboxSessionKey):
            return self.session_id == other.session_id 
        return False
    

class File(BaseModel):
    name: str
    content: bytes


class CodeboxOutput(BaseModel):
    output_type: str
    content: str
    files: Optional[List[File]] = None
    

class CodeboxInstallRequest(BaseModel):
    packagenames: List[str]