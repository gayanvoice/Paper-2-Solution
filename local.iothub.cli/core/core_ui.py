import pyfiglet
import logging

from model.configuration.shared_iot_configuration_model import SharedIotConfigurationModel


class CoreUi:
    @staticmethod
    def welcome(client_cli_session_uuid):
        iot_configuration_xml_file_path = "configuration/iot_configuration.xml"
        shared_iot_configuration_model = SharedIotConfigurationModel().get(iot_configuration_xml_file_path=iot_configuration_xml_file_path)
        if shared_iot_configuration_model.is_ur_cobot_dev_mode or shared_iot_configuration_model.is_robotiq_gripper_dev_mode:
            title = pyfiglet.figlet_format("local.iothub.cli", width=400)
            mode = pyfiglet.figlet_format("Test Mode", width=400)
            logging.info("\n{title} - {mode}".format(title=title, mode=mode))
            logging.info("session uuid - {session_uuid}".format(session_uuid=client_cli_session_uuid))
            logging.info("is_ur_cobot_dev_mode:{is_ur_cobot_dev_mode} / is_robotiq_gripper_dev_mode:{is_robotiq_gripper_dev_mode}"
                         .format(is_ur_cobot_dev_mode=shared_iot_configuration_model.is_ur_cobot_dev_mode,
                                 is_robotiq_gripper_dev_mode=shared_iot_configuration_model.is_robotiq_gripper_dev_mode))
        else:
            title = pyfiglet.figlet_format("local.iothub.cli", width=400)
            mode = pyfiglet.figlet_format("Production Mode", width=400)
            logging.info("\n{title} - {mode}".format(title=title, mode=mode))
            logging.info("cli session uuid - {cli_session_uuid}".format(
                cli_session_uuid=client_cli_session_uuid))
