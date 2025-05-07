import asyncio
import json
import logging
import random
import re
import time
import numpy as np
import uuid6
import pyodbc
from datetime import datetime, timezone

from core import core_global
from core.Device import Device
from model.configuration.shared_iot_configuration_model import SharedIotConfigurationModel
from model.configuration.robotiq_gripper_iot_configuration import RobotiqGripperIotConfigurationModel
from model.configuration.shared_sql_configuration_model import SharedSqlConfigurationModel
from model.response.activate_gripper_command_response_model import ActivateGripperCommandResponseModel
from model.response.close_gripper_command_response_model import CloseGripperCommandResponseModel
from model.response.open_gripper_command_response_model import OpenGripperCommandResponseModel
from robotiq_gripper.robotiq_gripper_controller import RobotiqGripperController

class RobotiqGripper:

    def __init__(self, client_cli_session_uuid):
        self.device = None
        self.robotiq_gripper_controller = None
        self.iot_configuration_xml_file_path = "configuration/iot_configuration.xml"
        self.sql_configuration_xml_file_path = "configuration/sql_configuration.xml"
        self.shared_iot_configuration_model = SharedIotConfigurationModel().get(
            iot_configuration_xml_file_path=self.iot_configuration_xml_file_path)
        self.robotiq_gripper_iot_configuration_model = RobotiqGripperIotConfigurationModel().get(
            iot_configuration_xml_file_path=self.iot_configuration_xml_file_path)
        self.sql_configuration_model = SharedSqlConfigurationModel().get(
            sql_configuration_xml_file_path=self.sql_configuration_xml_file_path)
        self.act = 0
        self.pos = 3
        self.uuid = uuid6.uuid8()
        self.numpy_dictionary = None
        self.client_cli_session_uuid = client_cli_session_uuid
        self.is_sql_running = False
        try:
            pyodbc_connection = self.get_pyodbc_connection()
            logging.info(f"robotiq gripper: connected to database: {pyodbc_connection.getinfo(pyodbc.SQL_SERVER_NAME)}")
        except Exception as e:
            logging.error(f"robotiq gripper: error occurred: {e}")

    def stdin_listener(self):
        while True:
            if core_global.is_queue_running is False and self.is_sql_running is False:
                break

    async def connect_robotiq_gripper_physical_device(self, robotiq_gripper_iot_configuration_model):
        self.robotiq_gripper_controller = RobotiqGripperController()
        self.robotiq_gripper_controller.connect(
            hostname=robotiq_gripper_iot_configuration_model.host,
            port=robotiq_gripper_iot_configuration_model.port,
            socket_timeout=robotiq_gripper_iot_configuration_model.socket_timeout)
        self.robotiq_gripper_controller.activate()

    async def connect_robotiq_gripper_iot_device(self, robotiq_gripper_iot_configuration_model):
        self.device = Device(model_id=robotiq_gripper_iot_configuration_model.model_id,
                             provisioning_host=robotiq_gripper_iot_configuration_model.provisioning_host,
                             id_scope=robotiq_gripper_iot_configuration_model.id_scope,
                             registration_id=robotiq_gripper_iot_configuration_model.registration_id,
                             symmetric_key=robotiq_gripper_iot_configuration_model.symmetric_key)
        await self.device.create_iot_hub_device_client()
        await self.device.iot_hub_device_client.connect()

    async def connect_azure_iot(self, queue):

        await self.connect_robotiq_gripper_iot_device(
            robotiq_gripper_iot_configuration_model=self.robotiq_gripper_iot_configuration_model)

        if self.shared_iot_configuration_model.is_robotiq_gripper_dev_mode is False:
            await self.connect_robotiq_gripper_physical_device(
                robotiq_gripper_iot_configuration_model=self.robotiq_gripper_iot_configuration_model)

        command_listeners = asyncio.gather(
            self.device.execute_command_listener(
                method_name="OpenGripperCommand",
                request_handler=self.open_gripper_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="CloseGripperCommand",
                request_handler=self.close_gripper_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="ActivateGripperCommand",
                request_handler=self.activate_gripper_command_request_handler,
                response_handler=self.command_response_handler,
            )
        )

        send_telemetry_task_to_database_task = None
        send_telemetry_task_to_cloud_task = None
        if self.shared_iot_configuration_model.is_robotiq_gripper_dev_mode:
            send_telemetry_task_to_port_task = asyncio.create_task(self.serving_interactive_server(mode="development"))
            if self.shared_iot_configuration_model.iot_client_mode == "cloud":
                send_telemetry_task_to_cloud_task = asyncio.create_task(self.send_telemetry_task_to_cloud(mode="development"))
            elif self.shared_iot_configuration_model.iot_client_mode == "local":
                send_telemetry_task_to_database_task = asyncio.create_task(self.send_telemetry_task_to_database(mode="development"))
        else:
            send_telemetry_task_to_port_task = asyncio.create_task(self.serving_interactive_server(mode="production"))
            if self.shared_iot_configuration_model.iot_client_mode == "cloud": send_telemetry_task_to_cloud_task = asyncio.create_task(self.send_telemetry_task_to_cloud(mode="production"))
            elif self.shared_iot_configuration_model.iot_client_mode == "local": send_telemetry_task_to_database_task = asyncio.create_task(self.send_telemetry_task_to_database(mode="production"))

        loop = asyncio.get_running_loop()
        user_finished = loop.run_in_executor(None, self.stdin_listener)
        await user_finished

        if not command_listeners.done():
            result = {'Status': 'Done'}
            command_listeners.set_result(list(result.values()))

        if self.shared_iot_configuration_model.is_robotiq_gripper_dev_mode is False:
            self.robotiq_gripper_controller.disconnect()
        command_listeners.cancel()

        if self.shared_iot_configuration_model.iot_client_mode == "local":
            send_telemetry_task_to_database_task.cancel()
        elif self.shared_iot_configuration_model.iot_client_mode == "cloud":
            send_telemetry_task_to_cloud_task.cancel()
        send_telemetry_task_to_port_task.cancel()

        await self.device.iot_hub_device_client.shutdown()
        await queue.put(None)

    @staticmethod
    def command_response_handler(command_response_model):
        return json.dumps(command_response_model, default=lambda o: o.__dict__, indent=1)

    async def activate_gripper(self, request_payload):
        activate_gripper_command_response_model = ActivateGripperCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_robotiq_gripper_dev_mode:
                self.act = 1
                time.sleep(1)
            else:
                self.robotiq_gripper_controller.activate()
            return activate_gripper_command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return activate_gripper_command_response_model.get_exception(str(ex)).to_json()

    async def activate_gripper_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.activate_gripper(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def open_gripper(self, request_payload):
        open_gripper_command_response_model = OpenGripperCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_robotiq_gripper_dev_mode:
                self.pos = 227
                time.sleep(1)
            else:
                self.robotiq_gripper_controller.open_gripper()
            return open_gripper_command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return open_gripper_command_response_model.get_exception(str(ex)).to_json()

    async def open_gripper_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.open_gripper(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def close_gripper(self, request_payload):
        close_gripper_command_response_model = CloseGripperCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_robotiq_gripper_dev_mode:
                self.pos = 3
                time.sleep(1)
            else:
                self.robotiq_gripper_controller.close_gripper()
            return close_gripper_command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return close_gripper_command_response_model.get_exception(str(ex)).to_json()

    async def close_gripper_command_request_handler(self,request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = await self.close_gripper(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler


    async def send_telemetry_task_to_cloud(self, mode="production"):
        while True:
            await asyncio.sleep(self.shared_iot_configuration_model.telemetry_delay)
            try:
                host_operation_start_time = datetime.now()
                self.uuid = uuid6.uuid8()
                if mode == "production":
                    logging.info("sending robotiq gripper production device telemetry task to cloud")
                    current_numpy_dictionary = self.get_production_telemetry(request_type="cloud")
                    iot_operation_start_time = time.time_ns()
                    await self.device.send_telemetry(telemetry=current_numpy_dictionary)
                    self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                  iot_operation_start_time=iot_operation_start_time,
                                                                  host_operation_start_time=host_operation_start_time)
                elif mode == "development":
                    logging.info("sending robotiq gripper development device telemetry task to cloud")
                    current_numpy_dictionary = self.get_development_telemetry(request_type="cloud")
                    iot_operation_start_time = time.time_ns()
                    await self.device.send_telemetry(telemetry=current_numpy_dictionary)
                    self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                  iot_operation_start_time=iot_operation_start_time,
                                                                  host_operation_start_time=host_operation_start_time)
            except Exception as e:
                logging.error(f"robotiq gripper: {e}")

    async def send_telemetry_task_to_database(self, mode="production"):
        while True:
            await asyncio.sleep(self.shared_iot_configuration_model.telemetry_delay)
            if self.shared_iot_configuration_model.iot_client_mode == "local":
                try:
                    host_operation_start_time = datetime.now()
                    self.uuid = uuid6.uuid8()
                    if mode == "production":
                        logging.info("robotiq gripper: sending robotiq gripper production device telemetry task to database")
                        current_numpy_dictionary = self.get_production_telemetry(request_type="local")
                        self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                      request_type="local",
                                                                      host_operation_start_time=host_operation_start_time)
                    elif mode == "development":
                        logging.info("robotiq gripper: sending robotiq gripper development device telemetry task to database")
                        current_numpy_dictionary = self.get_development_telemetry(request_type="local")
                        self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                      request_type="local",
                                                                      host_operation_start_time=host_operation_start_time)

                except Exception as e:
                    logging.error(f"robotiq gripper: {e}")

    async def robotiq_gripper_interactive_server(self, reader, writer, mode):
        try:
            addr = writer.get_extra_info('peername')
            client_ip, client_port = addr
            logging.info(f'robotiq gripper server connected by {client_ip}:{client_port}')

            data = await reader.read(100)
            command = data.decode('utf-8')

            host_operation_start_time = datetime.now()

            logging.info(f'robotiq gripper sever received: {command}')

            get_telemetry_pattern = r'\bget_telemetry\b'
            set_activate_gripper_pattern = r'\bset_activate_gripper\b'
            set_open_gripper = r'\bset_open_gripper\b'
            set_close_gripper = r'\bset_close_gripper\b'

            if re.search(get_telemetry_pattern, command):
                if mode == "production":
                    current_numpy_dictionary = self.get_production_telemetry()
                    message = json.dumps(current_numpy_dictionary, cls=NumpyEncoder)
                    writer.write(message.encode())
                    await writer.drain()
                    logging.info(f'sent robotiq gripper production {mode} telemetry task to port: {message}')
                    self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                  request_type="server",
                                                                  host_operation_start_time=host_operation_start_time)
                    await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_activate_gripper_pattern,
                                                         command_request_handler=command,
                                                         command_response_handler=message,
                                                         host_operation_start_time=host_operation_start_time)
                elif mode == "development":
                    current_numpy_dictionary = self.get_development_telemetry()
                    message = json.dumps(current_numpy_dictionary, cls=NumpyEncoder)
                    writer.write(message.encode())
                    await writer.drain()
                    logging.info(f'sent robotiq gripper development {mode} telemetry task to port: {message}')
                    self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                  request_type="server",
                                                                  host_operation_start_time=host_operation_start_time)
                    await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_activate_gripper_pattern,
                                                         command_request_handler=command,
                                                         command_response_handler=message,
                                                         host_operation_start_time=host_operation_start_time)
            elif re.search(set_activate_gripper_pattern, command):
                logging.info(command)
                command_response_handler = await self.activate_gripper(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_activate_gripper_pattern,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_open_gripper, command):
                logging.info(command)
                command_response_handler = await self.open_gripper(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_open_gripper,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_close_gripper, command):
                logging.info(command)
                command_response_handler = await self.close_gripper(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_close_gripper,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
        except Exception as ex:
            logging.error(ex)
        finally:
            writer.close()
            await writer.wait_closed()


    async def serving_interactive_server(self, mode="production"):
        server = await asyncio.start_server(
            lambda r, w: self.robotiq_gripper_interactive_server(r, w, mode),
            self.robotiq_gripper_iot_configuration_model.external_host,
            self.robotiq_gripper_iot_configuration_model.interactive_port)
        addr = server.sockets[0].getsockname()
        logging.info(f'serving robotiq gripper server on {addr}')
        async with server:
            await server.serve_forever()

    async def send_command_task_to_port(self, writer, mode, pattern, command_request_handler, command_response_handler,
                                        host_operation_start_time):
        # command_response_handler = json.dumps(command_response_handler, cls=NumpyEncoder)
        writer.write(command_response_handler.encode())
        await writer.drain()
        logging.info(f'sent robotiq gripper development {mode} command task {pattern} to port: {command_response_handler}')
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=command_request_handler,
                                                    command_response_handler=command_response_handler,
                                                    request_type="server",
                                                    host_operation_start_time=host_operation_start_time)

    def get_production_telemetry(self, request_type="cloud"):
        host_operation_start_time = time.time_ns()
        uuid = str(self.uuid)
        act = self.robotiq_gripper_controller.get_activate()
        gto = self.robotiq_gripper_controller.get_goto()
        force = self.robotiq_gripper_controller.get_force()
        spe = self.robotiq_gripper_controller.get_speed()
        pos = self.robotiq_gripper_controller.get_position()
        sta = self.robotiq_gripper_controller.get_status()
        pre = self.robotiq_gripper_controller.get_position_request()
        obj = self.robotiq_gripper_controller.get_object_detection()
        flt = self.robotiq_gripper_controller.get_fault()
        host_operation_time_elapsed = time.time_ns() - host_operation_start_time
        return {
            "uuid": uuid,
            "uuid_type": "uuid8",
            "request_type": request_type,
            "act": act,
            "gto": gto,
            "for": force,
            "spe": spe,
            "pos": pos,
            "sta": sta,
            "pre": pre,
            "obj": obj,
            "flt": flt,
            "host_operation_time_elapsed": host_operation_time_elapsed
        }

    def get_development_telemetry(self, request_type="cloud"):
        host_operation_start_time = time.time_ns()
        uuid = str(self.uuid)
        gto = random.randint(0, 1)
        force = random.randint(10, 100)
        spe = random.randint(10, 100)
        sta = random.randint(0, 3)
        pre = random.randint(3, 227)
        obj = random.randint(0, 3)
        flt = random.randint(0, 15)
        host_operation_time_elapsed = time.time_ns() - host_operation_start_time
        return {
            "uuid": uuid,
            "uuid_type": "uuid8",
            "request_type": request_type,
            "act": self.act,
            "gto": gto,
            "for": force,
            "spe": spe,
            "pos": self.pos,
            "sta": sta,
            "pre": pre,
            "obj": obj,
            "flt": flt,
            "host_operation_time_elapsed": host_operation_time_elapsed
        }

    def insert_telemetry_event_into_sql_database(self, telemetry_event, request_type=None,
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
                INSERT INTO device_telemetry_event_robotiq_gripper (
                    telemetry_event_uuid, uuid_type, request_type, origin, act, gto, [for], spe, pos, sta, pre, obj, flt,
                     host_operation_time_elapsed, sql_operation_time_elapsed, iot_operation_time_elapsed, 
                     client_cli_start_timestamp, client_cli_end_timestamp, client_cli_session_uuid
                ) VALUES (
                    '{self.escape_string(telemetry_event['uuid'])}', '{self.escape_string(telemetry_event['uuid_type'])}',
                    '{request_type}', 'local.iothub.cli',
                    '{self.escape_string(telemetry_event['act'])}', '{self.escape_string(telemetry_event['gto'])}',
                    '{self.escape_string(telemetry_event['for'])}', '{self.escape_string(telemetry_event['spe'])}',
                    '{self.escape_string(telemetry_event['pos'])}', '{self.escape_string(telemetry_event['sta'])}',
                    '{self.escape_string(telemetry_event['pre'])}', '{self.escape_string(telemetry_event['obj'])}',
                    '{self.escape_string(telemetry_event['flt'])}',
                    '{host_operation_time_elapsed}', '{sql_operation_time_elapsed}', '{iot_operation_time_elapsed}',
                     '{host_operation_start_time.strftime('%Y-%m-%d %H:%M:%S') + f'.{host_operation_start_time.microsecond // 1000:03d}'}',
                    '{datetime.now().strftime('%Y-%m-%d %H:%M:%S') + f'.{datetime.now().microsecond // 1000:03d}'}','{self.escape_string(self.client_cli_session_uuid)}'
                )
                """
                pyodbc_cursor.execute(insert_sql_query)

                logging.info(f"robotiq gripper: inserted device telemetry event {telemetry_event['uuid']} in {(time.time_ns() - sql_operation_start_time) / 1_000_000} ms")

                sql_commit_start_time = time.time_ns()

                update_sql_query = f"""UPDATE device_telemetry_event_robotiq_gripper 
                SET sql_operation_time_elapsed = '{time.time_ns() - sql_operation_start_time}' 
                WHERE telemetry_event_uuid = '{self.escape_string(telemetry_event['uuid'])}'"""

                pyodbc_cursor.execute(update_sql_query)
                pyodbc_cursor.close()

                pyodbc_connection.commit()

                logging.info(f"robotiq gripper: updated device telemetry event {telemetry_event['uuid']} in {(time.time_ns() - sql_commit_start_time) / 1_000_000} ms")
                self.is_sql_running = False
                return True
        except Exception as e:
            logging.error(f"robotiq gripper: error occurred: {e}")
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
                INSERT INTO device_command_event_robotiq_gripper (
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

                logging.info(f"robotiq gripper: inserted device command event {uuid} in {(time.time_ns() - sql_operation_start_time) / 1_000_000} ms")

                sql_commit_start_time = time.time_ns()

                update_sql_query = f"""UPDATE device_command_event_robotiq_gripper 
                SET sql_operation_time_elapsed = '{time.time_ns() - sql_operation_start_time}' 
                WHERE command_event_uuid = '{self.escape_string(uuid)}'"""

                pyodbc_cursor.execute(update_sql_query)

                pyodbc_cursor.close()
                pyodbc_connection.commit()

                logging.info(
                    f"robotiq gripper: updated device command event {uuid} in {(time.time_ns() - sql_commit_start_time) / 1_000_000} ms")
                self.is_sql_running = False
                return True
        except Exception as e:
            logging.error(f"robotiq gripper: error occurred: {e}")
            self.is_sql_running = False
            return False


    @staticmethod
    def has_values_changed(initial_values, current_values):
        try:
            for key, initial_value in initial_values.items():
                current_value = current_values.get(key)
                if key == "act":
                    if not np.isclose(current_value, initial_value):
                        logging.info(f"robotiq gripper: act not equal: {current_value} / {initial_value}")
                        return True
                elif key == "pos":
                    if not np.isclose(current_value, initial_value):
                        logging.info(f"robotiq gripper: pos not equal: {current_value} / {initial_value}")
                        return True
                    return False
        except Exception as e:
            logging.error(f"robotiq gripper: error occurred: {e}")
            return True

    @staticmethod
    def escape_string(value):
        try:
            return value.replace("'", "''")
        except Exception as e:
            return value

    def get_pyodbc_connection(self):
        return pyodbc.connect(self.sql_configuration_model.connection_string)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.generic):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
