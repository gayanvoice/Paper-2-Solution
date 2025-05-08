from dataclasses import dataclass
from typing import List

@dataclass
class ConditionalLlmRequestModel:
    if_check: str
    then_actions: List[str]
    else_actions: List[str]