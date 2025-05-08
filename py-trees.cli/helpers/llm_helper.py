import json

class LlmHelper:
    @staticmethod
    def is_if_else_statement(json_str: str) -> bool:
        try:
            data = json.loads(json_str)
            if "if" in data and "then" in data and "else" in data:
                if isinstance(data["then"], list) and isinstance(data["else"], list):
                    if all(isinstance(action, str) for action in data["then"]) and all(isinstance(action, str) for action in data["else"]):
                        return True
            return False
        except json.JSONDecodeError:
            return False
        
    @staticmethod
    def is_sequence_statement(json_str: str) -> bool:
        try:
            data = json.loads(json_str)
            return isinstance(data.get("sequence"), list) and \
                   all(isinstance(action, str) for action in data["sequence"])
        except (json.JSONDecodeError, KeyError):
            return False