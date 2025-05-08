from dataclasses import dataclass
from typing import List

@dataclass
class SequenceLlmRequestModel:
    action_sequence: List[str]