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
from model.configuration.gom_iot_configuration import GOMIotConfigurationModel
from model.configuration.shared_iot_configuration_model import SharedIotConfigurationModel
from model.configuration.robotiq_gripper_iot_configuration import RobotiqGripperIotConfigurationModel
from model.configuration.shared_sql_configuration_model import SharedSqlConfigurationModel
from model.response.activate_gripper_command_response_model import ActivateGripperCommandResponseModel
from model.response.close_gripper_command_response_model import CloseGripperCommandResponseModel
from model.response.open_gripper_command_response_model import OpenGripperCommandResponseModel
from model.response.start_gom_command_response_model import StartGomCommandResponseModel
from model.response.stop_gom_command_response_model import StopGomCommandResponseModel
from robotiq_gripper.robotiq_gripper_controller import RobotiqGripperController

class GOM:

    def __init__(self, client_cli_session_uuid):
        self.device = None
        self.gom_controller = None
        self.iot_configuration_xml_file_path = "configuration/iot_configuration.xml"
        self.sql_configuration_xml_file_path = "configuration/sql_configuration.xml"
        self.shared_iot_configuration_model = SharedIotConfigurationModel().get(
            iot_configuration_xml_file_path=self.iot_configuration_xml_file_path)
        self.gom_iot_configuration_model = GOMIotConfigurationModel().get(
            iot_configuration_xml_file_path=self.iot_configuration_xml_file_path)
        self.sql_configuration_model = SharedSqlConfigurationModel().get(
            sql_configuration_xml_file_path=self.sql_configuration_xml_file_path)
        self.is_gom_running = False
        self.gom_progress = 0
        self.uuid = uuid6.uuid8()
        self.numpy_dictionary = None
        self.client_cli_session_uuid = client_cli_session_uuid
        self.is_sql_running = False
        try:
            pyodbc_connection = self.get_pyodbc_connection()
            logging.info(f"gom: connected to database: {pyodbc_connection.getinfo(pyodbc.SQL_SERVER_NAME)}")
        except Exception as e:
            logging.error(f"gom: error occurred: {e}")

    def stdin_listener(self):
        while True:
            if core_global.is_queue_running is False and self.is_sql_running is False:
                break

    @staticmethod
    async def connect_gom_physical_device():
        logging.info("gom connecting, wait 5 seconds")
        time.sleep(5)
        logging.info("gom connected")

    async def connect_gom_iot_device(self, gom_iot_configuration_model):
        self.device = Device(model_id=gom_iot_configuration_model.model_id,
                             provisioning_host=gom_iot_configuration_model.provisioning_host,
                             id_scope=gom_iot_configuration_model.id_scope,
                             registration_id=gom_iot_configuration_model.registration_id,
                             symmetric_key=gom_iot_configuration_model.symmetric_key)
        await self.device.create_iot_hub_device_client()
        await self.device.iot_hub_device_client.connect()

    async def connect_azure_iot(self, queue):

        await self.connect_gom_iot_device(gom_iot_configuration_model=self.gom_iot_configuration_model)

        if self.shared_iot_configuration_model.is_gom_dev_mode:
            await self.connect_gom_physical_device()
        else:
            raise NotImplemented("gom is not implemented. dev mode only!")

        command_listeners = asyncio.gather(
            self.device.execute_command_listener(
                method_name="StartGomCommand",
                request_handler=self.start_gom_command_request_handler,
                response_handler=self.command_response_handler,
            ),
            self.device.execute_command_listener(
                method_name="StopGomCommand",
                request_handler=self.stop_gom_command_request_handler,
                response_handler=self.command_response_handler,
            )
        )

        send_telemetry_task_to_database_task = None
        send_telemetry_task_to_cloud_task = None
        if self.shared_iot_configuration_model.is_robotiq_gripper_dev_mode:
            send_telemetry_task_to_port_task = asyncio.create_task(self.serving_interactive_server(mode="development"))
            gom_process_task = asyncio.create_task(self.gom_process_task())
            if self.shared_iot_configuration_model.iot_client_mode == "cloud":
                send_telemetry_task_to_cloud_task = asyncio.create_task(self.send_telemetry_task_to_cloud(mode="development"))
            elif self.shared_iot_configuration_model.iot_client_mode == "local":
                send_telemetry_task_to_database_task = asyncio.create_task(self.send_telemetry_task_to_database(mode="development"))
        else:
            raise NotImplemented("gom is not implemented. dev mode only!")

        loop = asyncio.get_running_loop()
        user_finished = loop.run_in_executor(None, self.stdin_listener)
        await user_finished

        if not command_listeners.done():
            result = {'Status': 'Done'}
            command_listeners.set_result(list(result.values()))

        command_listeners.cancel()

        if self.shared_iot_configuration_model.iot_client_mode == "local":
            send_telemetry_task_to_database_task.cancel()
        elif self.shared_iot_configuration_model.iot_client_mode == "cloud":
            send_telemetry_task_to_cloud_task.cancel()
        gom_process_task.cancel()
        send_telemetry_task_to_port_task.cancel()

        await self.device.iot_hub_device_client.shutdown()
        await queue.put(None)

    @staticmethod
    def command_response_handler(command_response_model):
        return json.dumps(command_response_model, default=lambda o: o.__dict__, indent=1)

    async def start_gom(self, request_payload):
        activate_gripper_command_response_model = ActivateGripperCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_gom_dev_mode:
                time.sleep(1)
                self.is_gom_running = True
            else:
                raise NotImplemented("gom is not implemented. dev mode only!")
            return activate_gripper_command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return activate_gripper_command_response_model.get_exception(str(ex)).to_json()

    async def start_gom_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = self.start_gom(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def stop_gom(self, request_payload):
        start_gom_command_response_model = StartGomCommandResponseModel()
        try:
            if self.shared_iot_configuration_model.is_gom_dev_mode:
                time.sleep(1)
                self.is_gom_running = False
            else:
                raise NotImplemented("gom is not implemented. dev mode only!")
            return start_gom_command_response_model.get_successfully_executed().to_json()
        except Exception as ex:
            return start_gom_command_response_model.get_exception(str(ex)).to_json()

    async def stop_gom_command_request_handler(self, request_payload):
        host_operation_start_time = datetime.now()
        command_response_handler = self.stop_gom(request_payload=request_payload)
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=json.dumps(request_payload),
                                                    command_response_handler=command_response_handler,
                                                    request_type="cloud",
                                                    host_operation_start_time=host_operation_start_time)
        return command_response_handler

    async def send_telemetry_task_to_database(self, mode="production"):
        while True:
            await asyncio.sleep(self.shared_iot_configuration_model.telemetry_delay)
            if self.shared_iot_configuration_model.iot_client_mode == "local":
                try:
                    host_operation_start_time = datetime.now()
                    self.uuid = uuid6.uuid8()
                    if mode == "production":
                        raise NotImplemented("gom is not implemented. dev mode only!")
                    elif mode == "development":
                        logging.info("gom: sending gom development device telemetry task to database")
                        current_numpy_dictionary = self.get_development_telemetry(request_type="local")
                        self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                      request_type="local",
                                                                      host_operation_start_time=host_operation_start_time)

                except Exception as e:
                    logging.error(f"gom: {e}")

    async def send_telemetry_task_to_cloud(self, mode="production"):
        while True:
            await asyncio.sleep(self.shared_iot_configuration_model.telemetry_delay)
            try:
                host_operation_start_time = datetime.now()
                self.uuid = uuid6.uuid8()
                if mode == "production":
                    raise NotImplemented("gom is not implemented. dev mode only!")
                elif mode == "development":
                    logging.info("sending gom development device telemetry task to cloud")
                    current_numpy_dictionary = self.get_development_telemetry(request_type="cloud")
                    iot_operation_start_time = time.time_ns()
                    await self.device.send_telemetry(telemetry=current_numpy_dictionary)
                    self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                  request_type="cloud",
                                                                  iot_operation_start_time=iot_operation_start_time,
                                                                  host_operation_start_time=host_operation_start_time)
            except Exception as e:
                logging.error(f"gom: {e}")

    async def gom_process_task(self):
        while True:
            await asyncio.sleep(1)
            if self.is_gom_running:
                if self.gom_progress <= 100:
                    self.gom_progress = self.gom_progress + 1
                else:
                    self.is_gom_running = False
            else:
                self.gom_progress = 0

    async def gom_interactive_server(self, reader, writer, mode):
        try:
            addr = writer.get_extra_info('peername')
            client_ip, client_port = addr
            logging.info(f'gom daemon connected by {client_ip}:{client_port}')

            data = await reader.read(100)
            command = data.decode('utf-8')

            host_operation_start_time = datetime.now()

            logging.info(f'gom sever received: {command}')

            get_telemetry_pattern = r'\bget_telemetry\b'
            set_start_gom = r'\bset_start_gom\b'
            set_stop_gom = r'\bset_stop_gom\b'

            if re.search(get_telemetry_pattern, command):
                if mode == "production":
                    raise NotImplemented("gom is not implemented. dev mode only!")
                elif mode == "development":
                    current_numpy_dictionary = self.get_development_telemetry(request_type="local")
                    message = json.dumps(current_numpy_dictionary, cls=NumpyEncoder)
                    writer.write(message.encode())
                    await writer.drain()
                    logging.info(f'sent gom development {mode} telemetry task to port: {message}')
                    self.insert_telemetry_event_into_sql_database(telemetry_event=current_numpy_dictionary,
                                                                  request_type="server",
                                                                  host_operation_start_time=host_operation_start_time)
                    await self.send_command_task_to_port(writer=writer, mode=mode, pattern=get_telemetry_pattern,
                                                         command_request_handler=command,
                                                         command_response_handler=message,
                                                         host_operation_start_time=host_operation_start_time)
            elif re.search(set_start_gom, command):
                logging.info(command)
                command_response_handler = await self.start_gom(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_start_gom,
                                                     command_request_handler=command,
                                                     command_response_handler=command_response_handler,
                                                     host_operation_start_time=host_operation_start_time)
            elif re.search(set_stop_gom, command):
                logging.info(command)
                command_response_handler = await self.stop_gom(request_payload=None)
                await self.send_command_task_to_port(writer=writer, mode=mode, pattern=set_stop_gom,
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
            lambda r, w: self.gom_interactive_server(r, w, mode),
            self.gom_iot_configuration_model.external_host,
            self.gom_iot_configuration_model.interactive_port)
        addr = server.sockets[0].getsockname()
        logging.info(f'serving gom server on {addr}')
        async with server:
            await server.serve_forever()

    async def send_command_task_to_port(self, writer, mode, pattern, command_request_handler, command_response_handler,
                                        host_operation_start_time):
        # command_response_handler = json.dumps(command_response_handler, cls=NumpyEncoder)
        writer.write(command_response_handler.encode())
        await writer.drain()
        logging.info(f'sent gom development {mode} command task {pattern} to port: {command_response_handler}')
        self.insert_command_event_into_sql_database(uuid=str(self.uuid),
                                                    command_request_handler=command_request_handler,
                                                    command_response_handler=command_response_handler,
                                                    request_type="server",
                                                    host_operation_start_time=host_operation_start_time)

    def get_production_telemetry(self, request_type="cloud"):
        raise NotImplemented("gom is not implemented. dev mode only!")

    def get_development_telemetry(self, request_type="cloud"):
        host_operation_start_time = time.time_ns()
        uuid = str(self.uuid)
        is_gom_running = self.is_gom_running
        gom_progress = self.gom_progress
        host_operation_time_elapsed = time.time_ns() - host_operation_start_time
        return {
            "uuid": uuid,
            "uuid_type": "uuid8",
            "request_type": request_type,
            "is_gom_running": is_gom_running,
            "gom_progress": gom_progress,
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
                INSERT INTO device_telemetry_event_gom (
                    telemetry_event_uuid, uuid_type, request_type, origin, is_gom_running, gom_progress,
                     host_operation_time_elapsed, sql_operation_time_elapsed, iot_operation_time_elapsed, 
                     client_cli_start_timestamp, client_cli_end_timestamp, client_cli_session_uuid
                ) VALUES (
                    '{self.escape_string(telemetry_event['uuid'])}', '{self.escape_string(telemetry_event['uuid_type'])}',
                    '{request_type}', 'local.iothub.cli',
                    '{self.escape_string(telemetry_event['is_gom_running'])}', '{self.escape_string(telemetry_event['gom_progress'])}',
                    '{host_operation_time_elapsed}', '{sql_operation_time_elapsed}', '{iot_operation_time_elapsed}',
                    '{host_operation_start_time.strftime('%Y-%m-%d %H:%M:%S') + f'.{host_operation_start_time.microsecond // 1000:03d}'}',
                    '{datetime.now().strftime('%Y-%m-%d %H:%M:%S') + f'.{datetime.now().microsecond // 1000:03d}'}','{self.escape_string(self.client_cli_session_uuid)}'
                )
                """
                pyodbc_cursor.execute(insert_sql_query)

                logging.info(f"gom: inserted device telemetry event {telemetry_event['uuid']} in {(time.time_ns() - sql_operation_start_time) / 1_000_000} ms")

                sql_commit_start_time = time.time_ns()

                update_sql_query = f"""UPDATE device_telemetry_event_gom 
                SET sql_operation_time_elapsed = '{time.time_ns() - sql_operation_start_time}' 
                WHERE telemetry_event_uuid = '{self.escape_string(telemetry_event['uuid'])}'"""

                pyodbc_cursor.execute(update_sql_query)
                pyodbc_cursor.close()

                pyodbc_connection.commit()

                logging.info(
                    f"gom: updated device telemetry event {telemetry_event['uuid']} in {(time.time_ns() - sql_commit_start_time) / 1_000_000} ms")
                self.is_sql_running = False
                return True
        except Exception as e:
            logging.error(f"gom: error occurred: {e}")
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
                INSERT INTO device_command_event_gom (
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

                logging.info(f"gom: inserted device command event {uuid} in {(time.time_ns() - sql_operation_start_time) / 1_000_000} ms")

                sql_commit_start_time = time.time_ns()

                update_sql_query = f"""UPDATE device_command_event_gom 
                SET sql_operation_time_elapsed = '{time.time_ns() - sql_operation_start_time}' 
                WHERE command_event_uuid = '{self.escape_string(uuid)}'"""

                pyodbc_cursor.execute(update_sql_query)

                pyodbc_cursor.close()
                pyodbc_connection.commit()

                logging.info(
                    f"gom: updated device command event {uuid} in {(time.time_ns() - sql_commit_start_time) / 1_000_000} ms")
                self.is_sql_running = False
                return True
        except Exception as e:
            logging.error(f"gom: error occurred: {e}")
            self.is_sql_running = False
            return False

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
