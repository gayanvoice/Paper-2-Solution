from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import json

@dataclass
class ResponseModel:
    Status: Optional[bool] = None
    Message: Optional[str] = None
    IotElapsedTime: Optional[float] = None
    DtElapsedTime: Optional[float] = None
    
    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
