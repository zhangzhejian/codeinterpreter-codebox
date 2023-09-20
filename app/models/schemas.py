from pydantic import BaseModel
from typing import List, Optional
import json
import datetime
from enum import Enum

class ProgrammingLanguage(str,Enum):
    JUPYTER="JUPYTER"

class PortUsage(str, Enum):
    TCP = "TCP"
    EXPORT="EXPORT"
    JUPYTER="JUPYTER"


class PortOccupation(BaseModel):
    session_id: str
    usage: PortUsage=PortUsage.TCP
    