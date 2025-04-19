import xml.etree.ElementTree as ET


class SharedIotConfigurationModel:
    def __init__(self):
        self._telemetry_delay = None
        self._is_queue_running = None
        self._is_ur_cobot_dev_mode = None
        self._is_robotiq_gripper_dev_mode = None
        self._is_gom_dev_mode = None
        self._iot_client_mode = None

    @property
    def telemetry_delay(self):
        return self._telemetry_delay

    @property
    def is_queue_running(self):
        return self._is_queue_running

    @property
    def is_ur_cobot_dev_mode(self):
        return self._is_ur_cobot_dev_mode

    @property
    def is_robotiq_gripper_dev_mode(self):
        return self._is_robotiq_gripper_dev_mode


    @property
    def is_gom_dev_mode(self):
        return self._is_gom_dev_mode

    @property
    def iot_client_mode(self):
        return self._iot_client_mode


    @telemetry_delay.setter
    def telemetry_delay(self, value):
        self._telemetry_delay = float(value)

    @is_queue_running.setter
    def is_queue_running(self, value):
        self._is_queue_running = {"0": False, "1": True}[value]

    @is_ur_cobot_dev_mode.setter
    def is_ur_cobot_dev_mode(self, value):
        self._is_ur_cobot_dev_mode = {"0": False, "1": True}[value]


    @is_robotiq_gripper_dev_mode.setter
    def is_robotiq_gripper_dev_mode(self, value):
        self._is_robotiq_gripper_dev_mode = {"0": False, "1": True}[value]


    @is_gom_dev_mode.setter
    def is_gom_dev_mode(self, value):
        self._is_gom_dev_mode = {"0": False, "1": True}[value]

    @iot_client_mode.setter
    def iot_client_mode(self, value):
        self._iot_client_mode = value


    def get(self, iot_configuration_xml_file_path):
        iot_configuration_element_tree = ET.parse(iot_configuration_xml_file_path)
        self.telemetry_delay = iot_configuration_element_tree.find('./shared/telemetry_delay').text
        self.is_queue_running = iot_configuration_element_tree.find('./shared/is_queue_running').text
        self.is_ur_cobot_dev_mode = iot_configuration_element_tree.find('./shared/is_ur_cobot_dev_mode').text
        self.is_robotiq_gripper_dev_mode = iot_configuration_element_tree.find('./shared/is_robotiq_gripper_dev_mode').text
        self.is_gom_dev_mode = iot_configuration_element_tree.find('./shared/is_gom_dev_mode').text
        self.iot_client_mode = iot_configuration_element_tree.find('./shared/iot_client_mode').text
        return self
