import xml.etree.ElementTree as ET


class RobotiqGripperIotConfigurationModel:
    def __init__(self):
        self._model_id = None
        self._provisioning_host = None
        self._id_scope = None
        self._registration_id = None
        self._symmetric_key = None
        self._host = None
        self._port = None
        self._socket_timeout = None
        self._external_host = None
        self._interactive_port = None
        self._simulation_port = None

    @property
    def model_id(self):
        return self._model_id

    @property
    def provisioning_host(self):
        return self._provisioning_host

    @property
    def id_scope(self):
        return self._id_scope

    @property
    def registration_id(self):
        return self._registration_id

    @property
    def symmetric_key(self):
        return self._symmetric_key

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def socket_timeout(self):
        return self._socket_timeout

    @property
    def external_host(self):
        return self._external_host

    @property
    def interactive_port(self):
        return self._interactive_port


    @property
    def simulation_port(self):
        return self._simulation_port

    @model_id.setter
    def model_id(self, value):
        self._model_id = value

    @provisioning_host.setter
    def provisioning_host(self, value):
        self._provisioning_host = value

    @id_scope.setter
    def id_scope(self, value):
        self._id_scope = value

    @registration_id.setter
    def registration_id(self, value):
        self._registration_id = value

    @symmetric_key.setter
    def symmetric_key(self, value):
        self._symmetric_key = value

    @host.setter
    def host(self, value):
        self._host = value

    @port.setter
    def port(self, value):
        self._port = int(value)

    @socket_timeout.setter
    def socket_timeout(self, value):
        self._socket_timeout = float(value)


    @external_host.setter
    def external_host(self, value):
        self._external_host = str(value)


    @interactive_port.setter
    def interactive_port(self, value):
        self._interactive_port = int(value)

    @simulation_port.setter
    def simulation_port(self, value):
        self._simulation_port = int(value)


    def get(self, iot_configuration_xml_file_path):
        iot_configuration_element_tree = ET.parse(iot_configuration_xml_file_path)
        self.model_id = iot_configuration_element_tree.find('./robotiq_gripper/model_id').text
        self.provisioning_host = iot_configuration_element_tree.find('./robotiq_gripper/provisioning_host').text
        self.id_scope = iot_configuration_element_tree.find('./robotiq_gripper/id_scope').text
        self.registration_id = iot_configuration_element_tree.find('./robotiq_gripper/registration_id').text
        self.symmetric_key = iot_configuration_element_tree.find('./robotiq_gripper/symmetric_key').text
        self.host = iot_configuration_element_tree.find('./robotiq_gripper/host').text
        self.port = iot_configuration_element_tree.find('./robotiq_gripper/port').text
        self.socket_timeout = iot_configuration_element_tree.find('./robotiq_gripper/socket_timeout').text
        self.external_host = iot_configuration_element_tree.find('./robotiq_gripper/external_host').text
        self.interactive_port = iot_configuration_element_tree.find('./robotiq_gripper/interactive_port').text
        self.simulation_port = iot_configuration_element_tree.find('./robotiq_gripper/simulation_port').text
        return self