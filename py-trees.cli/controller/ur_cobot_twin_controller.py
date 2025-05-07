from typing import Optional, Dict, Any
import json
import time

from controller.robotiq_gripper_twin_controller import ResponseModel
from model.ur_cobot_twin_model import URCobotTwinModel

class URCobotTwinController:
    def __init__(self, digital_twins_client: str, digital_twin_id: str):
        self.digital_twin_id = digital_twin_id
        self.digital_twins_client = digital_twins_client

    def get_digital_twin(self) -> URCobotTwinModel:
        try:
            twin_dictionary = self.digital_twins_client.get_digital_twin(self.digital_twin_id)
            return URCobotTwinModel.from_dict(twin_dictionary)
        except Exception as e:
            print(f"get digital twin error: {e}")
            return None


    def move(self, base: float, shoulder: float, elbow: float, wrist1: float, wrist2: float, wrist3: float) -> ResponseModel:
        start_time = time.time()
        try:
            twin_state_before_update = self.get_digital_twin()
            json_patch = [
                {
                    "op": "replace",
                    "path": "/control_move_j/RequestPayload/IsCommandRequested",
                    "value": True
                },
                {
                    "op": "replace",
                    "path": "/control_move_j/Base",
                    "value": base
                },
                {
                    "op": "replace",
                    "path": "/control_move_j/Shoulder",
                    "value": shoulder
                },
                {
                    "op": "replace",
                    "path": "/control_move_j/Elbow",
                    "value": elbow
                },
                {
                    "op": "replace",
                    "path": "/control_move_j/Wrist1",
                    "value": wrist1
                },
                {
                    "op": "replace",
                    "path": "/control_move_j/Wrist2",
                    "value": wrist2
                },
                {
                    "op": "replace",
                    "path": "/control_move_j/Wrist3",
                    "value": wrist3
                },
                {
                    "op": "remove",
                    "path": "/control_move_j/ResponsePayload"
                }
            ]

            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)
            
            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_move_j.RequestPayload.IsCommandRequested:
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
            response_model.Message = twin_state_after_update.control_move_j.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_move_j.ResponsePayload.ElapsedTime
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


    def close_popup(self) -> ResponseModel:
        start_time = time.time()
        try:
            twin_state_before_update = self.get_digital_twin()
            json_patch = [
                {
                    "op": "replace",
                    "path": "/control_close_popup/RequestPayload/IsCommandRequested",
                    "value": True
                },
                {
                    "op": "remove",
                    "path": "/control_close_popup/ResponsePayload"
                }
            ]

            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)
            
            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_close_popup.RequestPayload.IsCommandRequested:
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
            response_model.Message = twin_state_after_update.control_close_popup.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_close_popup.ResponsePayload.ElapsedTime
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

    def open_popup(self, popup_text: str) -> ResponseModel:
        start_time = time.time()
        try:
            twin_state_before_update = self.get_digital_twin()
            json_patch = [
                {
                    "op": "replace",
                    "path": "/control_open_popup/RequestPayload/IsCommandRequested",
                    "value": True
                },
                {
                    "op": "replace",
                    "path": "/control_open_popup/PopupText",
                    "value": popup_text
                },
                {
                    "op": "remove",
                    "path": "/control_open_popup/ResponsePayload"
                }
            ]

            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)
            
            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_open_popup.RequestPayload.IsCommandRequested:
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
            response_model.Message = twin_state_after_update.control_open_popup.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_open_popup.ResponsePayload.ElapsedTime
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

    def start_free_drive(self) -> ResponseModel:
        start_time = time.time()
        try:
            twin_state_before_update = self.get_digital_twin()
            json_patch = [
                {
                    "op": "replace",
                    "path": "/control_start_free_drive/RequestPayload/IsCommandRequested",
                    "value": True
                },
                {
                    "op": "remove",
                    "path": "/control_start_free_drive/ResponsePayload"
                }
            ]

            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)
            
            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_start_free_drive.RequestPayload.IsCommandRequested:
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
            response_model.Message = twin_state_after_update.control_start_free_drive.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_start_free_drive.ResponsePayload.ElapsedTime
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

    def stop_free_drive(self) -> ResponseModel:
        start_time = time.time()
        try:
            twin_state_before_update = self.get_digital_twin()
            json_patch = [
                {
                    "op": "replace",
                    "path": "/control_stop_free_drive/RequestPayload/IsCommandRequested",
                    "value": True
                },
                {
                    "op": "remove",
                    "path": "/control_stop_free_drive/ResponsePayload"
                }
            ]

            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)
            
            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_stop_free_drive.RequestPayload.IsCommandRequested:
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
            response_model.Message = twin_state_after_update.control_stop_free_drive.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_stop_free_drive.ResponsePayload.ElapsedTime
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


    def power_off(self) -> ResponseModel:
        start_time = time.time()
        try:
            twin_state_before_update = self.get_digital_twin()
            json_patch = [
                {
                    "op": "replace",
                    "path": "/control_power_off/RequestPayload/IsCommandRequested",
                    "value": True
                },
                {
                    "op": "remove",
                    "path": "/control_power_off/ResponsePayload"
                }
            ]

            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)
            
            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_power_off.RequestPayload.IsCommandRequested:
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
            response_model.Message = twin_state_after_update.control_power_off.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_power_off.ResponsePayload.ElapsedTime
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

    def power_on(self) -> ResponseModel:
        start_time = time.time()
        try:
            twin_state_before_update = self.get_digital_twin()
            json_patch = [
                {
                    "op": "replace",
                    "path": "/control_power_on/RequestPayload/IsCommandRequested",
                    "value": True
                },
                {
                    "op": "remove",
                    "path": "/control_power_on/ResponsePayload"
                }
            ]

            self.digital_twins_client.update_digital_twin(self.digital_twin_id, json_patch)
            
            i = 1
            while True:
                twin_state_after_update = self.get_digital_twin()
                if twin_state_after_update.control_power_on.RequestPayload.IsCommandRequested:
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
            response_model.Message = twin_state_after_update.control_power_on.ResponsePayload.Message
            response_model.IotElapsedTime = twin_state_after_update.control_power_on.ResponsePayload.ElapsedTime
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