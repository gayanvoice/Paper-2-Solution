import json

from model.response.response_model import ResponseModel


class CloseGripperCommandResponseModel(ResponseModel):
    def __init__(self):
        super().__init__()
        self._status = None
        self._message = None

    def get_gripper_command_response_model(self, status):
        response_model = super().get(status=status)
        self._status = response_model.status
        return self

    def get_successfully_executed(self):
        self.get_gripper_command_response_model(status=True)
        self._message = "close gripper command executed successfully"
        return self

    def get_exception(self, exception):
        self.get_gripper_command_response_model(status=False)
        self._message = exception
        return self

    def to_json(self):
        return json.dumps({
            'status': self._status,
            'duration': self._duration,
            'message': self._message
        })
