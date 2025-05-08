from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import json

@dataclass
class RobotiqGripperDigitalTwinModel:
    @dataclass
    class RequestPayload:
        IsCommandRequested: Optional[bool] = None

    @dataclass
    class ResponsePayload:
        Status: Optional[bool] = None
        Message: Optional[str] = None
        ElapsedTime: Optional[float] = None

    @dataclass
    class CommandModel:
        RequestPayload: Optional['RobotiqGripperDigitalTwinModel.RequestPayload'] = None
        ResponsePayload: Optional['RobotiqGripperDigitalTwinModel.ResponsePayload'] = None

    dtId: str
    etag: str
    control_activate_gripper: CommandModel
    control_open_gripper: CommandModel
    control_close_gripper: CommandModel

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'RobotiqGripperDigitalTwinModel':
        def parse_gripper_command(cmd_data: Dict[str, Any]) -> 'RobotiqGripperDigitalTwinModel.CommandModel':
            request_payload = cmd_data.get('RequestPayload')
            response_payload = cmd_data.get('ResponsePayload')
            parsed_request_payload = RobotiqGripperDigitalTwinModel.RequestPayload(**request_payload) if request_payload else None
            parsed_response_payload = RobotiqGripperDigitalTwinModel.ResponsePayload(**response_payload) if response_payload else None
            return RobotiqGripperDigitalTwinModel.CommandModel(
                RequestPayload=parsed_request_payload,
                ResponsePayload=parsed_response_payload
            )

        return RobotiqGripperDigitalTwinModel(
            dtId=data.get('$dtId', ''),
            etag=data.get('$etag', ''),
            control_activate_gripper=parse_gripper_command(data.get('control_activate_gripper', {})),
            control_open_gripper=parse_gripper_command(data.get('control_open_gripper', {})),
            control_close_gripper=parse_gripper_command(data.get('control_close_gripper', {})),
        )
    
    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
