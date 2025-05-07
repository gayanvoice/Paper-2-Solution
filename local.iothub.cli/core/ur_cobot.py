import asyncio
import json
import math
import random
import re
import time
import numpy as np
import pyodbc
import URBasic
import logging
import uuid6

from datetime import datetime, timezone

from core import core_global
from core.Device import Device
from model.configuration.shared_iot_configuration_model import SharedIotConfigurationModel
from model.configuration.shared_sql_configuration_model import SharedSqlConfigurationModel
from model.configuration.ur_cobot_iot_configuration_model import URCobotIotConfigurationModel
from model.joint_position_model import JointPositionModel
from model.move_j_command_model import MoveJCommandModel
from model.response.close_popup_command_response_model import ClosePopupCommandResponseModel
from model.response.close_safety_popup_command_response_model import CloseSafetyPopupCommandResponseModel
from model.response.disable_free_drive_mode_command_response_model import DisableFreeDriveModeCommandResponseModel
from model.response.disable_teach_mode_command_response_model import DisableTeachModeCommandResponseModel
from model.response.enable_free_drive_mode_command_response_model import EnableFreeDriveModeCommandResponseModel
from model.response.enable_teach_mode_command_response_model import EnableTeachModeCommandResponseModel
from model.response.move_j_command_response_model import MoveJCommandResponseModel
from model.response.open_popup_command_response_model import OpenPopupCommandResponseModel
from model.response.pause_command_response_model import PauseCommandResponseModel
from model.response.play_command_response_model import PlayCommandResponseModel
from model.response.power_off_command_response_model import PowerOffCommandResponseModel
from model.response.power_on_command_response_model import PowerOnCommandResponseModel
from model.response.set_digital_output_command_response_model import SetDigitalOutputCommandResponseModel
from model.response.unlock_protective_stop_command_response_model import UnlockProtectiveStopCommandResponseModel

class URCobot:

    def __init__(self, client_cli_session_uuid):
        self.device = None
        self.ur_script_ext = None
        self.iot_configuration_xml_file_path = "configuration/iot_configuration.xml"
        self.sql_configuration_xml_file_path = "configuration/sql_configuration.xml"
        self.shared_iot_configuration_model = SharedIotConfigurationModel().get(
            iot_configuration_xml_file_path=self.iot_configuration_xml_file_path)
        self.ur_cobot_iot_configuration_model = URCobotIotConfigurationModel().get(
            iot_configuration_xml_file_path=self.iot_configuration_xml_file_path)
        self.sql_configuration_model = SharedSqlConfigurationModel().get(
            sql_configuration_xml_file_path=self.sql_configuration_xml_file_path)
        self.uuid = uuid6.uuid8()
        self.numpy_dictionary = None
        self.client_cli_session_uuid = client_cli_session_uuid
        self.is_sql_running = False
        try:
            pyodbc_connection = self.get_pyodbc_connection()
            logging.info(f"ur cobot: connected to database: {pyodbc_connection.getinfo(pyodbc.SQL_SERVER_NAME)}")
        except Exception as e:
            logging.error(f"ur cobot: error occurred: {e}")

    def stdin_listener(self):
        while True:
            if core_global.is_queue_running is False and self.is_sql_running is False:
                break

    def connect_ur_cobot_physical_device(self):
        robot_model = URBasic.robotModel.RobotModel()
        self.ur_script_ext = URBasic.urScriptExt.UrScriptExt(host=self.ur_cobot_iot_configuration_model.host,
                                                             robotModel=robot_model)
        self.ur_script_ext.reset_error()

    async def connect_ur_cobot_iot_device(self):
        self.device = Device(model_id=self.ur_cobot_iot_configuration_model.model_id,
                             provisioning_host=self.ur_cobot_iot_configuration_model.provisioning_host,
                             id_scope=self.ur_cobot_iot_configuration_model.id_scope,
                             registration_id=self.ur_cobot_iot_configuration_model.registration_id,
                             symmetric_key=self.ur_cobot_iot_configuration_model.symmetric_key)
        await self.device.create_iot_hub_device_client()
        await self.device.iot_hub_device_client.connect()

    async def connect_azure_iot(self, queue):
        await self.connect_ur_cobot_iot_device()

        if self.shared_iot_configuration_model.is_ur_cobot_dev_mode is False:
            try:
                self.connect_ur_cobot_physical_device()
                logging.info(f"ur cobot: successfully connected to the dashboard server")
            except Exception:
                logging.error(f"ur cobot: could not connect to the dashboard server")

        command_listeners = asyncio.gather(
            self.device.execute_command_listener(
                method_name="MoveJCommand",
                request_handler=self.move_j_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="PauseCommand",
                request_handler=self.pause_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="PlayCommand",
                request_handler=self.play_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="CloseSafetyPopupCommand",
                request_handler=self.close_safety_popup_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="UnlockProtectiveStopCommand",
                request_handler=self.unlock_protective_stop_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="OpenPopupCommand",
                request_handler=self.open_popup_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="ClosePopupCommand",
                request_handler=self.close_popup_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="PowerOnCommand",
                request_handler=self.power_on_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="PowerOffCommand",
                request_handler=self.power_off_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="StartFreeDriveModeCommand",
                request_handler=self.enable_free_drive_mode_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="StopFreeDriveModeCommand",
                request_handler=self.disable_free_drive_mode_command_request_handler,
                response_handler=self.command_response_handler,
            )
        )
        send_telemetry_task_to_database_task = None
        send_telemetry_task_to_cloud_task = None
        if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
            send_telemetry_task_to_port_task = asyncio.create_task(self.serving_interactive_server(mode="development"))
            if self.shared_iot_configuration_model.iot_client_mode == "cloud":
                send_telemetry_task_to_cloud_task = asyncio.create_task(
                    self.send_telemetry_task_to_cloud(mode="development"))
            elif self.shared_iot_configuration_model.iot_client_mode == "local":
                send_telemetry_task_to_database_task = asyncio.create_task(
                    self.send_telemetry_task_to_database(mode="development"))
        else:
            send_telemetry_task_to_port_task = asyncio.create_task(self.serving_interactive_server(mode="production"))
            if self.shared_iot_configuration_model.iot_client_mode == "cloud":
                send_telemetry_task_to_cloud_task = asyncio.create_task(
                    self.send_telemetry_task_to_cloud(mode="production"))
            elif self.shared_iot_configuration_model.iot_client_mode == "local":
                send_telemetry_task_to_database_task = asyncio.create_task(
                    self.send_telemetry_task_to_database(mode="production"))

        loop = asyncio.get_running_loop()
        user_finished = loop.run_in_executor(None, self.stdin_listener)
        await user_finished

        if not command_listeners.done():
            result = {'Status': 'Done'}
            command_listeners.set_result(list(result.values()))

        if self.shared_iot_configuration_model.is_ur_cobot_dev_mode is False:
            self.ur_script_ext.close()

        command_listeners.cancel()

        if self.shared_iot_configuration_model.iot_client_mode == "local":
            send_telemetry_task_to_database_task.cancel()
        elif self.shared_iot_configuration_model.iot_client_mode == "cloud":
            send_telemetry_task_to_cloud_task.cancel()
        send_telemetry_task_to_port_task.cancel()

        await self.device.iot_hub_device_client.shutdown()
        await queue.put(None)

    async def move_j_command(self, request_payload):
        command_response_model = MoveJCommandResponseModel()
        try:
            move_j_command_model = MoveJCommandModel.get_move_j_command_model_using_request_payload(request_payload)
            for joint_position_model in move_j_command_model.joint_position_model_array:
                joint_position_array = JointPositionModel.get_position_array_from_joint_position_model(
                    joint_position_model=joint_position_model
                )
                if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                    time.sleep(1)
                else:
                    self.ur_script_ext.movej(wait=True,
                                             q=joint_position_array,
                                             a=move_j_command_model.acceleration,
                                             v=move_j_command_model.velocity,
                                             t=move_j_command_model.time_s,
                                             r=move_j_command_model.blend_radius)
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()


    async def set_digital_output_command(self, output, value):
        command_response_model = SetDigitalOutputCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.set_standard_digital_out(n=output, b=value)
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()


    async def move_j_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.move_j_command(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    @staticmethod
    def command_response_handler(command_response_model):
        return json.dumps(command_response_model, default=lambda o: o.__dict__, indent=1)

    async def pause_command(self, request_payload):
        command_response_model = PauseCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.pause()
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()

    async def pause_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.pause_command(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def play_command(self, request_payload):
        command_response_model = PlayCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.play()
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()

    async def play_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.play_command(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def close_safety_popup_command(self, request_payload):
        command_response_model = CloseSafetyPopupCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.close_safety_popup()
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()

    async def close_safety_popup_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.close_safety_popup_command(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def unlock_protective_stop(self, request_payload):
        command_response_model = UnlockProtectiveStopCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.unlock_protective_stop()
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()

    async def unlock_protective_stop_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.unlock_protective_stop(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def open_popup_command(self, request_payload):
        command_response_model = OpenPopupCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.open_popup(popup_text=request_payload['popup_text'])
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()

    async def open_popup_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.open_popup_command(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def close_popup_command(self, request_payload):
        command_response_model = ClosePopupCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.close_popup()
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()

    async def close_popup_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.close_popup_command(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def power_on_command(self, request_payload):
        command_response_model = PowerOnCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.power_on()
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()

    async def power_on_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.power_on_command(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def power_off_command(self, request_payload):
        command_response_model = PowerOffCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.power_off()
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()

    async def power_off_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.power_off_command(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def enable_free_drive_mode_command(self, request_payload):
        command_response_model = EnableFreeDriveModeCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.enable_free_drive_mode()
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()

    async def enable_free_drive_mode_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.enable_free_drive_mode_command(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def disable_free_drive_mode_command(self, request_payload):
        command_response_model = DisableFreeDriveModeCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.disable_free_drive_mode()
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()

    async def disable_free_drive_mode_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.disable_free_drive_mode_command(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def enable_teach_mode_command(self, request_payload):
        command_response_model = EnableTeachModeCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.enable_teach_mode()
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()

    async def enable_teach_mode_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.enable_teach_mode_command(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def disable_teach_mode_command(self, request_payload):
        command_response_model = DisableTeachModeCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_ur_cobot_dev_mode:
                time.sleep(1)
            else:
                self.ur_script_ext.disable_teach_mode()
            return command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return command_response_model.get_exception(str(ex)).to_json()

    async def disable_teach_mode_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.disable_teach_mode_command(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def send_telemetry_task_to_cloud(self, mode="production"):
        while True:
            await asyncio.sleep(self.shared_iot_configuration_model.telemetry_delay)
            if self.shared_iot_configuration_model.iot_client_mode == "cloud":
                try:
                    host_operation_start_time = datetime.now()
                    self.uuid = uuid6.uuid8()
                    if mode == "production":
                        logging.info("ur cobot: sending ur cobot production device telemetry task to cloud")
                        logging.info([math.degrees(value) for value in self.ur_script_ext.get_actual_q()])
                        current_numpy_dictionary = self.get_production_telemetry(request_type="cloud")
                        iot_operation_start_time = time.time_ns()
                        await self.device.send_telemetry(telemetry=current_numpy_dictionary)
                        self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                      request_type="cloud",
                                                                      iot_operation_start_time=iot_operation_start_time,
                                                                      host_operation_start_time=host_operation_start_time)
                    elif mode == "development":
                        logging.info("ur cobot: sending ur cobot development device telemetry task to cloud")
                        current_numpy_dictionary = self.get_development_telemetry(request_type="cloud")
                        iot_operation_start_time = time.time_ns()
                        await self.device.send_telemetry(telemetry=current_numpy_dictionary)
                        self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                      request_type="cloud",
                                                                      iot_operation_start_time=iot_operation_start_time,
                                                                      host_operation_start_time=host_operation_start_time)
                except Exception as e:
                    logging.error(f"ur cobot: {e}")

    async def send_telemetry_task_to_database(self, mode="production"):
        while True:
            await asyncio.sleep(self.shared_iot_configuration_model.telemetry_delay)
            if self.shared_iot_configuration_model.iot_client_mode == "local":
                try:
                    host_operation_start_time = datetime.now()
                    self.uuid = uuid6.uuid8()
                    if mode == "production":
                        logging.info("ur cobot: sending ur cobot production device telemetry task to database")
                        logging.info([math.degrees(value) for value in self.ur_script_ext.get_actual_q()])
                        current_numpy_dictionary = self.get_production_telemetry(request_type="local")
                        self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                      request_type="local",
                                                                      host_operation_start_time=host_operation_start_time)
                    elif mode == "development":
                        logging.info("ur cobot: sending ur cobot development device telemetry task to database")
                        current_numpy_dictionary = self.get_development_telemetry(request_type="local")
                        self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                      request_type="local",
                                                                      host_operation_start_time=host_operation_start_time)

                except Exception as e:
                    logging.error(f"ur cobot: {e}")

    async def ur_cobot_interactive_server(self, reader, writer, mode):
        try:

            self.uuid = uuid6.uuid8()
            addr = writer.get_extra_info('peername')
            client_ip, client_port = addr
            logging.info(f'ur cobot sever connected by {client_ip}:{client_port}')

            data = await reader.read(100)
            command = data.decode('utf-8')

            host_operation_start_time = datetime.now()

            logging.info(f'ur cobot sever received: {command}')

            get_telemetry_pattern = r'\bget_telemetry\b'
            set_move_j_pattern = r'\bset_move_j\b'
            set_close_safety_popup_pattern = r'\bset_close_safety_popup\b'
            set_unlock_protective_stop_pattern = r'\bset_unlock_protective_stop\b'
            set_open_popup_pattern = r'\bset_open_popup\b'
            set_close_popup_pattern = r'\bset_close_popup\b'
            set_play_pattern = r'\bset_play\b'
            set_pause_pattern = r'\bset_pause\b'
            set_enable_free_drive_pattern = r'\bset_enable_free_drive\b'
            set_disable_free_drive_pattern = r'\bset_disable_free_drive\b'
            set_power_on_pattern = r'\bset_power_on\b'
            set_power_off_pattern = r'\bset_power_off\b'

            set_digital_output_pattern = r'\bset_digital_output\b'

            if re.search(get_telemetry_pattern, command):
                if mode == "production":
                    current_numpy_dictionary = self.get_production_telemetry(request_type="server")
                    message = json.dumps(current_numpy_dictionary, cls=NumpyEncoder)
                    writer.write(message.encode())
                    await writer.drain()
                    logging.info(f'sent ur cobot production {mode} telemetry task to port: {message}')
                    self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                  request_type="server",
                                                                  host_operation_start_time=host_operation_start_time)
                    await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_move_j_pattern,
                                                         command_request_handler=command,
                                                         command_response_handler=message,
                                                         host_operation_start_time=host_operation_start_time)
                elif mode == "development":
                    current_numpy_dictionary = self.get_development_telemetry(request_type="server")
                    message = json.dumps(current_numpy_dictionary, cls=NumpyEncoder)
                    writer.write(message.encode())
                    await writer.drain()
                    logging.info(f'sent ur cobot development {mode} telemetry task to port: {message}')
                    self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                  request_type="server",
                                                                  host_operation_start_time=host_operation_start_time)
                    await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_move_j_pattern,
                                                         command_request_handler=command,
                                                         command_response_handler=message,
                                                         host_operation_start_time=host_operation_start_time)
            elif re.search(set_move_j_pattern, command):
                logging.info(command)
                set_open_popup_pattern = r'set_move_j\(([^)]*)\)'
                match_move_j = re.search(set_open_popup_pattern, command)
                string_move_j = match_move_j.group(1)
                joint_position_model_array = [float(num) for num in string_move_j.split(',')]
                command_request_handler = {"_acceleration": 0.1, "_velocity": 0.1, "_time_s": 0, "_blend_radius": 0,
                                           "_joint_position_model_array": [{"JointPositionModel": {
                                               "Base": joint_position_model_array[0],
                                               "Shoulder": joint_position_model_array[1],
                                               "Elbow": joint_position_model_array[2],
                                               "Wrist1": joint_position_model_array[3],
                                               "Wrist2": joint_position_model_array[4],
                                               "Wrist3": joint_position_model_array[5]
                                           }}]}
                command_response_handler = await self.move_j_command(request_payload=command_request_handler)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_move_j_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_digital_output_pattern, command):
                logging.info(command)
                set_digital_output_pattern = r'set_digital_output\(([^)]*)\)'
                set_digital_output = re.search(set_digital_output_pattern, command)
                string_args = set_digital_output.group(1)
                args_array = [int(num) for num in string_args.split(',')]
                command_response_handler = await self.set_digital_output_command(output=args_array[0], value=args_array[1])
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_digital_output_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_close_safety_popup_pattern, command):
                logging.info(command)
                command_response_handler = await self.close_safety_popup_command(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_close_safety_popup_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_unlock_protective_stop_pattern, command):
                logging.info(command)
                command_response_handler = await self.unlock_protective_stop(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode,
                                                     pattern=set_unlock_protective_stop_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_open_popup_pattern, command):
                logging.info(command)
                set_open_popup_pattern = r'set_open_popup\("([^"]*)"\)'
                match_open_popup = re.search(set_open_popup_pattern, command)
                command_request_handler = {"popup_text": match_open_popup.group(1)}
                command_response_handler = await self.open_popup_command(request_payload=command_request_handler)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_open_popup_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_close_popup_pattern, command):
                logging.info(command)
                command_response_handler = await self.close_popup_command(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_close_popup_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_play_pattern, command):
                logging.info(command)
                command_response_handler = await self.play_command(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_play_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_pause_pattern, command):
                logging.info(command)
                command_response_handler = await self.pause_command(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_pause_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_enable_free_drive_pattern, command):
                logging.info(command)
                command_response_handler = await self.enable_free_drive_mode_command(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_enable_free_drive_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_disable_free_drive_pattern, command):
                logging.info(command)
                command_response_handler = await self.disable_free_drive_mode_command(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_disable_free_drive_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_power_on_pattern, command):
                logging.info(command)
                command_response_handler = await self.power_on_command(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_power_on_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_power_off_pattern, command):
                logging.info(command)
                command_response_handler = await self.power_off_command(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_power_off_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            else:
                logging.info(f'invalid command {command}')

        except Exception as ex:
            logging.error(ex)
        finally:
            writer.close()
            await writer.wait_closed()

    async def serving_interactive_server(self, mode="production"):
        logging.info(f'executing send_telemetry_task_to_port()')
        try:
            server = await asyncio.start_server(
                lambda r, w: self.ur_cobot_interactive_server(r, w, mode),
                self.ur_cobot_iot_configuration_model.external_host,
                self.ur_cobot_iot_configuration_model.interactive_port)
            addr = server.sockets[0].getsockname()
            logging.info(f'ur cobot server serving on {addr}')
            async with server:
                await server.serve_forever()

        except Exception as e:
            logging.error(f'ur cobot server error: {e}')
            raise

    async def send_command_task_to_port(self, writer, mode, pattern, command_request_handler, command_response_handler,
                                        host_operation_start_time):
        writer.write(command_response_handler.encode())
        await writer.drain()
        logging.info(f'sent ur cobot development {mode} command task {pattern} to port: {command_response_handler}')
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=command_request_handler,
                                                    command_response_handler=command_response_handler,
                                                    request_type="server",
                                                    host_operation_start_time=host_operation_start_time)

    def get_production_telemetry(self, request_type="cloud"):
        host_operation_start_time = time.time_ns()
        uuid = str(self.uuid)
        uuid_type = "uuid8"
        target_q = self.ur_script_ext.get_target_q()
        target_qd = self.ur_script_ext.get_target_qd()
        target_qdd = self.ur_script_ext.get_target_qdd()
        target_current = self.ur_script_ext.get_target_current()
        target_moment = self.ur_script_ext.get_target_moment()
        actual_current = self.ur_script_ext.get_actual_current()
        actual_q = self.ur_script_ext.get_actual_q()
        actual_qd = self.ur_script_ext.get_actual_qd()
        joint_control_output = self.ur_script_ext.get_joint_control_output()
        actual_tcp_force = self.ur_script_ext.get_actual_tcp_force()
        joint_temperatures = self.ur_script_ext.get_joint_temperatures()
        joint_mode = self.ur_script_ext.get_joint_mode()
        actual_tool_accelerometer = self.ur_script_ext.get_actual_tool_accelerometer()
        speed_scaling = self.ur_script_ext.get_speed_scaling()
        actual_momentum = self.ur_script_ext.get_actual_momentum()
        actual_main_voltage = self.ur_script_ext.get_actual_main_voltage()
        actual_robot_voltage = self.ur_script_ext.get_actual_robot_voltage()
        actual_robot_current = self.ur_script_ext.get_actual_robot_current()
        actual_joint_voltage = self.ur_script_ext.get_actual_joint_voltage()
        runtime_state = self.ur_script_ext.get_run_time_state()
        robot_mode = self.ur_script_ext.get_robot_mode()
        safety_mode = self.ur_script_ext.get_safety_mode()
        analog_io_types = self.ur_script_ext.get_analog_io_types()
        io_current = self.ur_script_ext.get_io_current()
        tool_mode = self.ur_script_ext.get_tool_mode()
        tool_output_voltage = self.ur_script_ext.get_tool_output_voltage()
        tool_output_current = self.ur_script_ext.get_tool_output_current()
        standard_analog_out_0 = self.ur_script_ext.get_standard_analog_out(n=0)
        standard_analog_out_1 = self.ur_script_ext.get_standard_analog_out(n=1)
        standard_digital_out_0 = self.ur_script_ext.get_standard_digital_out(n=0)
        standard_digital_out_1 = self.ur_script_ext.get_standard_digital_out(n=1)
        standard_digital_out_2 = self.ur_script_ext.get_standard_digital_out(n=2)
        standard_digital_out_3 = self.ur_script_ext.get_standard_digital_out(n=3)
        standard_digital_out_4 = self.ur_script_ext.get_standard_digital_out(n=4)
        standard_digital_out_5 = self.ur_script_ext.get_standard_digital_out(n=5)
        standard_digital_out_6 = self.ur_script_ext.get_standard_digital_out(n=6)
        standard_digital_out_7 = self.ur_script_ext.get_standard_digital_out(n=7)
        host_operation_time_elapsed = time.time_ns() - host_operation_start_time

        return {
            "uuid": uuid,
            "uuid_type": uuid_type,
            "request_type": request_type,
            "target_q": target_q,
            "target_qd": target_qd,
            "target_qdd": target_qdd,
            "target_current": target_current,
            "target_moment": target_moment,
            "actual_current": actual_current,
            "actual_q": actual_q,
            "actual_qd": actual_qd,
            "joint_control_output": joint_control_output,
            "actual_tcp_force": actual_tcp_force,
            "joint_temperatures": joint_temperatures,
            "joint_mode": joint_mode,
            "actual_tool_accelerometer": actual_tool_accelerometer,
            "speed_scaling": speed_scaling,
            "actual_momentum": actual_momentum,
            "actual_main_voltage": actual_main_voltage,
            "actual_robot_voltage": actual_robot_voltage,
            "actual_robot_current": actual_robot_current,
            "actual_joint_voltage": actual_joint_voltage,
            "runtime_state": runtime_state,
            "robot_mode": robot_mode,
            "safety_mode": safety_mode,
            "analog_io_types": analog_io_types,
            "io_current": io_current,
            "tool_mode": tool_mode,
            "tool_output_voltage": tool_output_voltage,
            "tool_output_current": tool_output_current,
            "standard_analog_out_0": standard_analog_out_0,
            "standard_analog_out_1": standard_analog_out_1,
            "standard_digital_out_0": standard_digital_out_0,
            "standard_digital_out_1": standard_digital_out_1,
            "standard_digital_out_2": standard_digital_out_2,
            "standard_digital_out_3": standard_digital_out_3,
            "standard_digital_out_4": standard_digital_out_4,
            "standard_digital_out_5": standard_digital_out_5,
            "standard_digital_out_6": standard_digital_out_6,
            "standard_digital_out_7": standard_digital_out_7,
            "host_operation_time_elapsed": host_operation_time_elapsed,
        }

    def get_development_telemetry(self, request_type="cloud"):
        host_operation_start_time = time.time_ns()
        uuid = str(self.uuid)
        uuid_type = "uuid8"
        target_q = [random.uniform(-1.8, 1.8) for _ in range(6)]
        target_qd = [random.uniform(-1.8, 1.8) for _ in range(6)]
        target_qdd = [random.uniform(-1.8, 1.8) for _ in range(6)]
        target_current = [random.uniform(-3.0, 3.0) for _ in range(6)]
        target_moment = [random.uniform(-90.0, 90.0) for _ in range(6)]
        actual_current = [random.uniform(-3.0, 3.0) for _ in range(6)]
        actual_q = [random.uniform(-1.8, 1.8) for _ in range(6)]
        actual_qd = [random.uniform(-1.8, 1.8) for _ in range(6)]
        joint_control_output = [random.uniform(0.0, 3.0) for _ in range(6)]
        actual_tcp_force = [random.uniform(0.0, 1.8) for _ in range(6)]
        joint_temperatures = [random.uniform(24.0, 25.5) for _ in range(6)]
        joint_mode = [random.uniform(253, 255) for _ in range(6)]
        actual_tool_accelerometer = [random.uniform(-10.0, 2.0) for _ in range(3)]
        speed_scaling = random.uniform(0.0, 0.5)
        actual_momentum = random.uniform(0.0, 0.5)
        actual_main_voltage = random.uniform(48.0, 48.5)
        actual_robot_voltage = random.uniform(48.0, 48.5)
        actual_robot_current = random.uniform(0.0, 0.5)
        actual_joint_voltage = [random.uniform(-0.5, 0.5) for _ in range(6)]
        runtime_state = random.randint(0, 1)
        robot_mode = random.randint(0, 7)
        safety_mode = random.randint(0, 1)
        analog_io_types = random.randint(0, 3)
        io_current = random.uniform(0.0, 0.5)
        tool_mode = random.randint(253, 255)
        tool_output_voltage = random.randint(0, 1)
        tool_output_current = random.uniform(0.0, 0.5)
        standard_analog_out_0 = random.uniform(0.0, 10.0)
        standard_analog_out_1 = random.uniform(0.0, 10.0)
        standard_digital_out_0 = random.randint(0, 1)
        standard_digital_out_1 = random.randint(0, 1)
        standard_digital_out_2 = random.randint(0, 1)
        standard_digital_out_3 = random.randint(0, 1)
        standard_digital_out_4 = random.randint(0, 1)
        standard_digital_out_5 = random.randint(0, 1)
        standard_digital_out_6 = random.randint(0, 1)
        standard_digital_out_7 = random.randint(0, 1)
        host_operation_time_elapsed = time.time_ns() - host_operation_start_time
        return {
            "uuid": uuid,
            "uuid_type": uuid_type,
            "request_type": request_type,
            "target_q": target_q,
            "target_qd": target_qd,
            "target_qdd": target_qdd,
            "target_current": target_current,
            "target_moment": target_moment,
            "actual_current": actual_current,
            "actual_q": actual_q,
            "actual_qd": actual_qd,
            "joint_control_output": joint_control_output,
            "actual_tcp_force": actual_tcp_force,
            "joint_temperatures": joint_temperatures,
            "joint_mode": joint_mode,
            "actual_tool_accelerometer": actual_tool_accelerometer,
            "speed_scaling": speed_scaling,
            "actual_momentum": actual_momentum,
            "actual_main_voltage": actual_main_voltage,
            "actual_robot_voltage": actual_robot_voltage,
            "actual_robot_current": actual_robot_current,
            "actual_joint_voltage": actual_joint_voltage,
            "runtime_state": runtime_state,
            "robot_mode": robot_mode,
            "safety_mode": safety_mode,
            "analog_io_types": analog_io_types,
            "io_current": io_current,
            "tool_mode": tool_mode,
            "tool_output_voltage": tool_output_voltage,
            "tool_output_current": tool_output_current,
            "standard_analog_out_0": standard_analog_out_0,
            "standard_analog_out_1": standard_analog_out_1,
            "standard_digital_out_0": standard_digital_out_0,
            "standard_digital_out_1": standard_digital_out_1,
            "standard_digital_out_2": standard_digital_out_2,
            "standard_digital_out_3": standard_digital_out_3,
            "standard_digital_out_4": standard_digital_out_4,
            "standard_digital_out_5": standard_digital_out_5,
            "standard_digital_out_6": standard_digital_out_6,
            "standard_digital_out_7": standard_digital_out_7,
            "host_operation_time_elapsed": host_operation_time_elapsed
        }

    def insert_telemetry_event_into_sql_database(self, telemetry_event,
                                                 request_type=None,
                                                 iot_operation_start_time=None,
                                                 host_operation_start_time=None):
        self.is_sql_running = True
        sql_operation_start_time = time.time_ns()
        try:
            with self.get_pyodbc_connection() as pyodbc_connection:
                pyodbc_cursor = pyodbc_connection.cursor()
                if request_type is None:
                    request_type = self.escape_string(telemetry_event['request_type'])

                host_operation_time_elapsed = time.time_ns() - int(host_operation_start_time.timestamp() * 1e9)

                if iot_operation_start_time is None:
                    iot_operation_time_elapsed = 0
                else:
                    iot_operation_time_elapsed = time.time_ns() - iot_operation_start_time

                sql_operation_time_elapsed = 0

                insert_sql_query = f"""
                INSERT INTO device_telemetry_event_ur_cobot (
                    telemetry_event_uuid, uuid_type, request_type, origin, target_q, target_qd, target_qdd,
                    target_current, target_moment, actual_current, actual_q, actual_qd, 
                    joint_control_output, actual_tcp_force, joint_temperatures, joint_mode, 
                    actual_tool_accelerometer, speed_scaling, actual_momentum, actual_main_voltage, 
                    actual_robot_voltage, actual_robot_current, actual_joint_voltage, runtime_state, 
                    robot_mode, safety_mode, analog_io_types, io_current, tool_mode, tool_output_voltage, 
                    tool_output_current, standard_analog_out_0, standard_analog_out_1, standard_digital_out_0, 
                    standard_digital_out_1, standard_digital_out_2, standard_digital_out_3, standard_digital_out_4, 
                    standard_digital_out_5, standard_digital_out_6, standard_digital_out_7, host_operation_time_elapsed,
                     sql_operation_time_elapsed, iot_operation_time_elapsed, 
                     client_cli_start_timestamp, client_cli_end_timestamp, client_cli_session_uuid 
                     ) VALUES (
                    '{self.escape_string(telemetry_event['uuid'])}', '{self.escape_string(telemetry_event['uuid_type'])}',
                    '{request_type}', 'local.iothub.cli',
                    '{self.escape_string(telemetry_event['target_q'])}', '{self.escape_string(telemetry_event['target_qd'])}',
                    '{self.escape_string(telemetry_event['target_qdd'])}', '{self.escape_string(telemetry_event['target_current'])}',
                    '{self.escape_string(telemetry_event['target_moment'])}', '{self.escape_string(telemetry_event['actual_current'])}',
                    '{self.escape_string(telemetry_event['actual_q'])}', '{self.escape_string(telemetry_event['actual_qd'])}',
                    '{self.escape_string(telemetry_event['joint_control_output'])}', '{self.escape_string(telemetry_event['actual_tcp_force'])}',
                    '{self.escape_string(telemetry_event['joint_temperatures'])}', '{self.escape_string(telemetry_event['joint_mode'])}',
                    '{self.escape_string(telemetry_event['actual_tool_accelerometer'])}', '{self.escape_string(telemetry_event['speed_scaling'])}',
                    '{self.escape_string(telemetry_event['actual_momentum'])}', '{self.escape_string(telemetry_event['actual_main_voltage'])}',
                    '{self.escape_string(telemetry_event['actual_robot_voltage'])}', '{self.escape_string(telemetry_event['actual_robot_current'])}',
                    '{self.escape_string(telemetry_event['actual_joint_voltage'])}', '{self.escape_string(telemetry_event['runtime_state'])}',
                    '{self.escape_string(telemetry_event['robot_mode'])}', '{self.escape_string(telemetry_event['safety_mode'])}',
                    '{self.escape_string(telemetry_event['analog_io_types'])}', '{self.escape_string(telemetry_event['io_current'])}',
                    '{self.escape_string(telemetry_event['tool_mode'])}', '{self.escape_string(telemetry_event['tool_output_voltage'])}',
                    '{self.escape_string(telemetry_event['tool_output_current'])}', '{self.escape_string(telemetry_event['standard_analog_out_0'])}',
                    '{self.escape_string(telemetry_event['standard_analog_out_1'])}', '{self.escape_string(telemetry_event['standard_digital_out_0'])}',
                    '{self.escape_string(telemetry_event['standard_digital_out_1'])}', '{self.escape_string(telemetry_event['standard_digital_out_2'])}',
                    '{self.escape_string(telemetry_event['standard_digital_out_3'])}', '{self.escape_string(telemetry_event['standard_digital_out_4'])}',
                    '{self.escape_string(telemetry_event['standard_digital_out_5'])}', '{self.escape_string(telemetry_event['standard_digital_out_6'])}',
                    '{self.escape_string(telemetry_event['standard_digital_out_7'])}',
                    '{host_operation_time_elapsed}', '{sql_operation_time_elapsed}', '{iot_operation_time_elapsed}',
                    '{host_operation_start_time.strftime('%Y-%m-%d %H:%M:%S') + f'.{host_operation_start_time.microsecond // 1000:03d}'}',
                    '{datetime.now().strftime('%Y-%m-%d %H:%M:%S') + f'.{datetime.now().microsecond // 1000:03d}'}', '{self.escape_string(self.client_cli_session_uuid)}'
                )
                """

                pyodbc_cursor.execute(insert_sql_query)
    

                logging.info(f"ur cobot: inserted device telemetry event {telemetry_event['uuid']} in {(time.time_ns() - sql_operation_start_time) / 1_000_000} ms")

                sql_commit_start_time = time.time_ns()

                update_sql_query = f"""UPDATE device_telemetry_event_ur_cobot 
                SET sql_operation_time_elapsed = '{time.time_ns() - sql_operation_start_time}' 
                WHERE telemetry_event_uuid = '{self.escape_string(telemetry_event['uuid'])}'"""

                pyodbc_cursor.execute(update_sql_query)

                pyodbc_cursor.close()
                pyodbc_connection.commit()

                logging.info(
                    f"ur cobot: updated device telemetry event {telemetry_event['uuid']} in {(time.time_ns() - sql_commit_start_time) / 1_000_000} ms")
                self.is_sql_running = False
                return True
        except Exception as e:
            logging.error(f"ur cobot: error occurred: {e}")
            self.is_sql_running = False
            return False

    def insert_command_event_into_sql_database(self, uuid, command_request_handler, command_response_handler,
                                               request_type, host_operation_start_time, iot_operation_start_time=None):
        self.is_sql_running = True
        sql_operation_start_time = time.time_ns()
        try:
            with self.get_pyodbc_connection() as pyodbc_connection:
                pyodbc_cursor = pyodbc_connection.cursor()

                if iot_operation_start_time is None:
                    iot_operation_time_elapsed = 0
                else:
                    iot_operation_time_elapsed = time.time_ns() - iot_operation_start_time

                host_operation_time_elapsed = time.time_ns() - int(host_operation_start_time.timestamp() * 1e9)

                sql_operation_time_elapsed = 0

                insert_sql_query = f"""
                INSERT INTO device_command_event_ur_cobot (
                    command_event_uuid, uuid_type, request_type, origin, command_request_handler, command_response_handler, host_operation_time_elapsed,
                     sql_operation_time_elapsed, iot_operation_time_elapsed, client_cli_start_timestamp, client_cli_end_timestamp, client_cli_session_uuid 
                     ) VALUES (
                    '{uuid}', 'uuid8', '{request_type}', 'local.iothub.cli', 
                    '{command_request_handler}',
                    '{command_response_handler}',
                    '{host_operation_time_elapsed}', '{sql_operation_time_elapsed}', '{iot_operation_time_elapsed}',
                    '{host_operation_start_time.strftime('%Y-%m-%d %H:%M:%S') + f'.{host_operation_start_time.microsecond // 1000:03d}'}',
                    '{datetime.now().strftime('%Y-%m-%d %H:%M:%S') + f'.{datetime.now().microsecond // 1000:03d}'}', '{self.escape_string(self.client_cli_session_uuid)}'
                )
                """

                pyodbc_cursor.execute(insert_sql_query)

                logging.info(f"ur cobot: inserted device command event {uuid} in {(time.time_ns() - sql_operation_start_time) / 1_000_000} ms")

                sql_commit_start_time = time.time_ns()

                update_sql_query = f"""UPDATE device_command_event_ur_cobot 
                SET sql_operation_time_elapsed = '{time.time_ns() - sql_operation_start_time}' 
                WHERE command_event_uuid = '{self.escape_string(uuid)}'"""

                pyodbc_cursor.execute(update_sql_query)

                pyodbc_cursor.close()
                pyodbc_connection.commit()

                logging.info(
                    f"ur cobot: updated device command event {uuid} in {(time.time_ns() - sql_commit_start_time) / 1_000_000} ms")
                self.is_sql_running = False
                return True
        except Exception as e:
            logging.error(f"ur cobot: error occurred: {e}")
            self.is_sql_running = False
            return False

    @staticmethod
    def escape_string(value):
        try:
            return value.replace("'", "''")
        except Exception as e:
            return value

    @staticmethod
    def has_values_changed(initial_values, current_values):
        try:
            for key, initial_value in initial_values.items():
                current_value = current_values.get(key)
                if key == "actual_q":
                    if not np.allclose(current_value, initial_value):
                        logging.info(f"actual_q not equal: {current_value} / {initial_value}")
                        return True
                elif key == "standard_analog_out_0":
                    if not np.isclose(current_value, initial_value):
                        logging.info(f"standard_analog_out_0 not equal: {current_value} / {initial_value}")
                        return True
                elif key == "standard_analog_out_1":
                    if not np.isclose(current_value, initial_value):
                        logging.info(f"standard_analog_out_1 not equal: {current_value} / {initial_value}")
                        return True
                elif key == "standard_digital_out_0":
                    if not current_value == initial_value:
                        logging.info(f"standard_digital_out_0 not equal: {current_value} / {initial_value}")
                        return True
                elif key == "standard_digital_out_1":
                    if not current_value == initial_value:
                        logging.info(f"standard_digital_out_1 not equal: {current_value} / {initial_value}")
                        return True
                elif key == "standard_digital_out_2":
                    if not current_value == initial_value:
                        logging.info(f"standard_digital_out_2 not equal: {current_value} / {initial_value}")
                        return True
                elif key == "standard_digital_out_3":
                    if not current_value == initial_value:
                        logging.info(f"standard_digital_out_3 not equal: {current_value} / {initial_value}")
                        return True
                    return False
        except Exception as e:
            logging.error(f"error occurred: {e}")
            return True

    def get_pyodbc_connection(self):
        return pyodbc.connect(self.sql_configuration_model.connection_string)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.generic):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
