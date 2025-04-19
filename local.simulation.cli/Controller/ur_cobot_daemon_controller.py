import asyncio
import json
import logging
from Model.ur_cobot_daemon_output_model import URCobotDaemonOutputModel


class URCobotDaemonController:
    def __init__(self):
        self.localhost = '127.0.0.1'
        self.ur_cobot_daemon_port = 50001

    async def get_ur_cobot_daemon_output_model(self):
        try:
            reader, writer = await asyncio.open_connection(self.localhost, self.ur_cobot_daemon_port)
            logging.info(f'ur cobot daemon controller connected to {self.localhost}:{self.ur_cobot_daemon_port}')
            request = "get_telemetry"
            writer.write(request.encode())
            await writer.drain()
            while True:

                data = await reader.read(4096)
                if not data:
                    break

                message = data.decode()
                telemetry_data = json.loads(message)
                logging.info(f'received telemetry data: {telemetry_data}')
                ur_cobot_daemon_output_model = URCobotDaemonOutputModel()
                ur_cobot_daemon_output_model.standard_analog_out_0 = telemetry_data['standard_analog_out_0']
                ur_cobot_daemon_output_model.standard_analog_out_1 = telemetry_data['standard_analog_out_1']
                ur_cobot_daemon_output_model.standard_digital_out_0 = telemetry_data['standard_digital_out_0']
                ur_cobot_daemon_output_model.standard_digital_out_1 = telemetry_data['standard_digital_out_1']
                ur_cobot_daemon_output_model.standard_digital_out_2 = telemetry_data['standard_digital_out_2']
                ur_cobot_daemon_output_model.standard_digital_out_3 = telemetry_data['standard_digital_out_3']
                ur_cobot_daemon_output_model.standard_digital_out_4 = telemetry_data['standard_digital_out_4']
                ur_cobot_daemon_output_model.standard_digital_out_5 = telemetry_data['standard_digital_out_5']
                ur_cobot_daemon_output_model.standard_digital_out_6 = telemetry_data['standard_digital_out_6']
                ur_cobot_daemon_output_model.standard_digital_out_7 = telemetry_data['standard_digital_out_7']
                logging.info(f'received telemetry data: {json.dumps(ur_cobot_daemon_output_model, default=default_serializer, indent=4)}')
                return ur_cobot_daemon_output_model

            writer.close()
            await writer.wait_closed()
            logging.info(f'connection to ur cobot daemon controller {self.localhost}:{self.ur_cobot_daemon_port} closed')

        except Exception as e:
            logging.error(f'error: {e}')


def default_serializer(obj):
    if isinstance(obj, URCobotDaemonOutputModel):
        return obj.__dict__  # Convert instance attributes to dictionary
    raise TypeError(f'Object of type {type(obj)} is not JSON serializable')
