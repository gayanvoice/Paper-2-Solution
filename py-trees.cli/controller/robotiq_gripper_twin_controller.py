import time
import json
from typing import Optional, Dict, Any
from azure.digitaltwins.core import DigitalTwinsClient

from model.behaviour_trees.response_model import ResponseModel
from model.robotiq_gripper_twin_model import RobotiqGripperTwinModel

class RobotiqGripperTwinController:
    def __init__(self, digital_twins_client: DigitalTwinsClient, digital_twin_id: str):
        self.digital_twin_id = digital_twin_id
        self.digital_twins_client = digital_twins_client

    def get_digital_twin(self) -> RobotiqGripperTwinModel:
        try:
            twin_dictionary = self.digital_twins_client.get_digital_twin(self.digital_twin_id)
            return RobotiqGripperTwinModel.from_dict(twin_dictionary)
        except Exception as e:
            print(f"get digital twin error: {e}")
            return None

    def activate(self) -> ResponseModel:
        start_time = time.time()
        try:
            twin_state_before_update = self.get_digital_twin()
            json_patch = [
                {
                    "op": "replace",
                    "path": "/control_activate_gripper/RequestPayload/IsCommandRequested",
                    "value": True
                },
                {
                    "op": "remove",
                    "path": "/control_activate_gripper/ResponsePayload"
                }
            ]

            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)
            
            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_activate_gripper.RequestPayload.IsCommandRequested:
                    print(f"waiting for {i} second(s)")
                    time.sleep(1)
                    i += 1
                else:
                    break;

            twin_state_after_update = self.get_digital_twin()

            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000

            response_model = ResponseModel()
            response_model.Status = True
            response_model.Message = twin_state_after_update.control_activate_gripper.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_activate_gripper.ResponsePayload.ElapsedTime
            response_model.DtElapsedTime = elapsed_ms
            return response_model
        except Exception as e:
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000

            response_model = ResponseModel()
            response_model.Status = False
            response_model.Message = str(e)
            response_model.IotElapsedTime = 0.0
            response_model.DtElapsedTime = elapsed_ms
            return response_model

    def open_gripper(self) -> ResponseModel:
        start_time = time.time()
        try:
            json_patch = [
                {
                    "op": "replace",
                    "path": "/control_open_gripper/RequestPayload/IsCommandRequested",
                    "value": True
                },
                {
                    "op": "remove",
                    "path": "/control_open_gripper/ResponsePayload"
                }
            ]
            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)

            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_open_gripper.RequestPayload.IsCommandRequested:
                    print(f"waiting for {i} second(s)")
                    time.sleep(1)
                    i += 1
                else:
                    break;

            twin_state_after_update = self.get_digital_twin()

            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000

            response_model = ResponseModel()
            response_model.Status = True
            response_model.Message = twin_state_after_update.control_open_gripper.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_open_gripper.ResponsePayload.ElapsedTime
            response_model.DtElapsedTime = elapsed_ms
            return response_model
        except Exception as e:
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000

            response_model = ResponseModel()
            response_model.Status = False
            response_model.Message = str(e)
            response_model.IotElapsedTime = 0.0
            response_model.DtElapsedTime = elapsed_ms
            return response_model

    def close_gripper(self) -> ResponseModel:
        start_time = time.time()
        try:
            json_patch = [
                {
                    "op": "replace",
                    "path": "/control_close_gripper/RequestPayload/IsCommandRequested",
                    "value": True
                },
                {
                    "op": "remove",
                    "path": "/control_close_gripper/ResponsePayload"
                }
            ]
            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)
            
            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_close_gripper.RequestPayload.IsCommandRequested:
                    print(f"waiting for {i} second(s)")
                    time.sleep(1)
                    i += 1
                else:
                    break;

            twin_state_after_update = self.get_digital_twin()

            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000

            response_model = ResponseModel()
            response_model.Status = True
            response_model.Message = twin_state_after_update.control_close_gripper.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_close_gripper.ResponsePayload.ElapsedTime
            response_model.DtElapsedTime = elapsed_ms
            return response_model
        except Exception as e:
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000

            response_model = ResponseModel()
            response_model.Status = False
            response_model.Message = str(e)
            response_model.IotElapsedTime = 0.0
            response_model.DtElapsedTime = elapsed_ms
            return response_model
