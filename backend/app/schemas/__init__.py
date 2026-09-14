from pydantic import BaseModel, Field
from typing import Optional, Any
class DeviceUpdate(BaseModel): power: Optional[bool]=None; brightness: Optional[int]=Field(None, ge=0, le=100); level: Optional[str]=None
class IntentRequest(BaseModel): message: str = Field(min_length=2, max_length=500)
class Action(BaseModel): device_id: str; device: str; action: str; value: Any=None
class ApplyRequest(BaseModel): actions: list[Action]
class ObjectSearch(BaseModel): query: str = Field(min_length=2, max_length=200)
class CompareRequest(BaseModel): previous_id: int; current_id: int
class AutomationCreate(BaseModel): name: str; trigger: str; actions: list[dict]; explanation: str='Created in NESTIQ'
class DemoEvent(BaseModel): room: str='Study Room'; event_type: str='User entered room'
