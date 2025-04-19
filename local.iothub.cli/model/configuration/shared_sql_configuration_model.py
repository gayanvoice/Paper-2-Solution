import xml.etree.ElementTree as ET


class SharedSqlConfigurationModel:
    def __init__(self):
        self._connection_string = None

    @property
    def connection_string(self):
        return self._connection_string


    @connection_string.setter
    def connection_string(self, value):
        self._connection_string = str(value)


    def get(self, sql_configuration_xml_file_path):
        sql_configuration_element_tree = ET.parse(sql_configuration_xml_file_path)
        self.connection_string = sql_configuration_element_tree.find('./shared/connection_string').text
        return self
