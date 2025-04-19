import socket
import struct
import time


class PrimaryClientController:
    # ANALOG VARIABLES
    ANALOG_OUT_0 = 0
    ANALOG_OUT_1 = 1

    # DIGITAL VARIABLES
    DIGITAL_OUT_0 = '0'
    DIGITAL_OUT_1 = 1
    DIGITAL_OUT_2 = 2
    DIGITAL_OUT_3 = 3

    ENCODING = 'UTF-8'

    def __init__(self):
        self.socket = None

    def connect(self, hostname, port=30002, socket_timeout=2.0):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((hostname, port))
        self.socket.settimeout(socket_timeout)

    def disconnect(self):
        self.socket.close()
        self.socket = None

    def is_connected(self):
        if self.socket:
            try:
                self.socket.send(b'\n')
                return True
            except socket.error:
                return False
        return False

    def send_digital_value(self, output, value):
        if not isinstance(output, int):
            raise ValueError(f"output {output} is invalid. output must be a numeric int.")
        if not isinstance(value, int):
            raise ValueError(f"value {value} is invalid. value must be a numeric int.")
        if not (value == 0 or value == 1):
            raise ValueError(f"value {value} is invalid. value must be either 0 or 1.")
        command = self.set_digital_command(output=output, value=value)
        return self.send_all(command=command)


    def send_analog_value(self, output, value):
        if not isinstance(output, int):
            raise ValueError(f"output {output} is invalid. output must be a numeric int.")
        if not isinstance(value, float):
            raise ValueError(f"value {value} is invalid. value must be a numeric float.")
        if value < 0:
            raise ValueError(f"value {value} is invalid. value must be non-negative float.")

        command = self.set_analog_command(output=output, value=value)
        return self.send_all(command=command)

    def send_all(self, command):
        try:
            self.socket.sendall(command)
            return True
        except Exception:
            return False


    @staticmethod
    def set_analog_command(output, value):
        return b'set_analog_out(' + str(output).encode() + b', ' + str(value).encode() + b')\n'

    @staticmethod
    def set_digital_command(output, value):
        return b'set_digital_out(' + str(output).encode() + b', ' + str(value).encode() + b')\n'
