import time
import json

import multiprocessing
import multiprocessing.connection

from typing import Optional, Dict, Any
from azure.digitaltwins.core import DigitalTwinsClient

from models.behaviour_trees.response_model import ResponseModel
from models.digital_twins.robotiq_gripper_digital_twin_model import RobotiqGripperDigitalTwinModel

class RobotiqGripperDigitalTwinController:
    def __init__(self, digital_twins_client: DigitalTwinsClient, digital_twin_id: str):
        self.digital_twin_id = digital_twin_id
        self.digital_twins_client = digital_twins_client

    def get_digital_twin(self) -> RobotiqGripperDigitalTwinModel:
        try:
            twin_dictionary = self.digital_twins_client.get_digital_twin(self.digital_twin_id)
            return RobotiqGripperDigitalTwinModel.from_dict(twin_dictionary)
        except Exception as e:
            print(f"get digital twin error: {e}")
            return None

    def activate(self, pipe_connection: multiprocessing.connection.Connection) -> None:
        pipe_connection.recv()
        percentage_complete = 0

        try:
            start_time = time.time()
            response_model = {}
            percentage_complete += 10
            pipe_connection.send([percentage_complete, response_model])

            twin_state_before_update = self.get_digital_twin()

            percentage_complete += 10
            pipe_connection.send([percentage_complete, response_model])

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
            
            percentage_complete += 10
            pipe_connection.send([percentage_complete, response_model])

            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)
            
            percentage_complete += 10
            pipe_connection.send([percentage_complete, response_model])

            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_activate_gripper.RequestPayload.IsCommandRequested:
                    percentage_complete += 1
                    pipe_connection.send([percentage_complete, response_model])
                    time.sleep(1)
                    i += 1
                else:
                    break;
            
            percentage_complete += 90 - percentage_complete
            pipe_connection.send([percentage_complete, response_model])

            twin_state_after_update = self.get_digital_twin()
            
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000

            response_model = ResponseModel()
            response_model.Status = True
            response_model.Message = twin_state_after_update.control_activate_gripper.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_activate_gripper.ResponsePayload.ElapsedTime
            response_model.DtElapsedTime = elapsed_ms

            percentage_complete = 100
            pipe_connection.send([percentage_complete, response_model])

        except Exception as e:
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000

            response_model = ResponseModel()
            response_model.Status = False
            response_model.Message = str(e)
            response_model.IotElapsedTime = 0.0
            response_model.DtElapsedTime = elapsed_ms
            
            percentage_complete = 100
            pipe_connection.send([percentage_complete, response_model])


    def open(self, pipe_connection: multiprocessing.connection.Connection) -> None:
        pipe_connection.recv()
        percentage_complete = 0

        try:
            start_time = time.time()
            response_model = {}
            percentage_complete += 10
            pipe_connection.send([percentage_complete, response_model])

            twin_state_before_update = self.get_digital_twin()

            percentage_complete += 10
            pipe_connection.send([percentage_complete, response_model])

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
            
            percentage_complete += 10
            pipe_connection.send([percentage_complete, response_model])

            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)
            
            percentage_complete += 10
            pipe_connection.send([percentage_complete, response_model])

            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_open_gripper.RequestPayload.IsCommandRequested:
                    percentage_complete += 1
                    pipe_connection.send([percentage_complete, response_model])
                    time.sleep(1)
                    i += 1
                else:
                    break;
            
            percentage_complete += 90 - percentage_complete
            pipe_connection.send([percentage_complete, response_model])

            twin_state_after_update = self.get_digital_twin()
            
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000

            response_model = ResponseModel()
            response_model.Status = True
            response_model.Message = twin_state_after_update.control_open_gripper.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_open_gripper.ResponsePayload.ElapsedTime
            response_model.DtElapsedTime = elapsed_ms

            percentage_complete = 100
            pipe_connection.send([percentage_complete, response_model])

        except Exception as e:
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000

            response_model = ResponseModel()
            response_model.Status = False
            response_model.Message = str(e)
            response_model.IotElapsedTime = 0.0
            response_model.DtElapsedTime = elapsed_ms
            
            percentage_complete = 100
            pipe_connection.send([percentage_complete, response_model])


    def close(self, pipe_connection: multiprocessing.connection.Connection) -> None:
        pipe_connection.recv()
        percentage_complete = 0

        try:
            start_time = time.time()
            response_model = {}
            percentage_complete += 10
            pipe_connection.send([percentage_complete, response_model])

            twin_state_before_update = self.get_digital_twin()

            percentage_complete += 10
            pipe_connection.send([percentage_complete, response_model])

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
            
            percentage_complete += 10
            pipe_connection.send([percentage_complete, response_model])

            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)
            
            percentage_complete += 10
            pipe_connection.send([percentage_complete, response_model])

            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_close_gripper.RequestPayload.IsCommandRequested:
                    percentage_complete += 1
                    pipe_connection.send([percentage_complete, response_model])
                    time.sleep(1)
                    i += 1
                else:
                    break;
            
            percentage_complete += 90 - percentage_complete
            pipe_connection.send([percentage_complete, response_model])

            twin_state_after_update = self.get_digital_twin()
            
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000

            response_model = ResponseModel()
            response_model.Status = True
            response_model.Message = twin_state_after_update.control_close_gripper.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_close_gripper.ResponsePayload.ElapsedTime
            response_model.DtElapsedTime = elapsed_ms

            percentage_complete = 100
            pipe_connection.send([percentage_complete, response_model])

        except Exception as e:
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000

            response_model = ResponseModel()
            response_model.Status = False
            response_model.Message = str(e)
            response_model.IotElapsedTime = 0.0
            response_model.DtElapsedTime = elapsed_ms
            
            percentage_complete = 100
            pipe_connection.send([percentage_complete, response_model])
    
