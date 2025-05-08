from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import json

@dataclass
class URCobotDigitalTwinModel:
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

        RequestPayload: Optional['URCobotDigitalTwinModel.RequestPayload'] = None
        ResponsePayload: Optional['URCobotDigitalTwinModel.ResponsePayload'] = None

    dtId: str
    etag: str
    control_move_j: CommandModel
    control_open_popup: CommandModel
    control_close_popup: CommandModel
    control_close_safety_popup: CommandModel
    control_power_off: CommandModel
    control_power_on: CommandModel
    control_start_free_drive: CommandModel
    control_stop_free_drive: CommandModel
    control_unlock_protective_stop: CommandModel

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> CommandModel:
        def parse_command(cmd_data: Dict[str, Any]) -> URCobotDigitalTwinModel.CommandModel:
            request_payload = cmd_data.get('RequestPayload')
            response_payload = cmd_data.get('ResponsePayload')
            parsed_request_payload = URCobotDigitalTwinModel.RequestPayload(**request_payload) if request_payload else None
            parsed_response_payload = URCobotDigitalTwinModel.ResponsePayload(**response_payload) if response_payload else None
            return URCobotDigitalTwinModel.CommandModel(
                RequestPayload=parsed_request_payload,
                ResponsePayload=parsed_response_payload
            )

        return URCobotDigitalTwinModel(
            dtId=data.get('$dtId', ''),
            etag=data.get('$etag', ''),
            control_move_j=parse_command(data.get('control_move_j', {})),
            control_open_popup=parse_command(data.get('control_open_popup', {})),
            control_close_popup=parse_command(data.get('control_close_popup', {})),
            control_close_safety_popup=parse_command(data.get('control_close_safety_popup', {})),
            control_power_off=parse_command(data.get('control_power_off', {})),
            control_power_on=parse_command(data.get('control_power_on', {})),
            control_start_free_drive=parse_command(data.get('control_start_free_drive', {})),
            control_stop_free_drive=parse_command(data.get('control_stop_free_drive', {})),
            control_unlock_protective_stop=parse_command(data.get('control_unlock_protective_stop', {})),
        )
       
    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
