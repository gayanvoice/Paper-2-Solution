from AddQual import addqual_global
from AddQual.addqual_global import is_ur_cobot_dev_mode, is_robotiq_gripper_dev_mode
import logging
import pyfiglet


class UI:
    def __init__(self):
        self.socket = None

    @staticmethod
    def welcome():
        if addqual_global.is_ur_cobot_dev_mode or addqual_global.is_robotiq_gripper_dev_mode:
            title = pyfiglet.figlet_format("local iothub cli", width=200)
            mode = pyfiglet.figlet_format("development mode", width=200)
            logging.info("\n{title}\n{mode}".format(title=title, mode=mode))
            logging.info("\nis_ur_cobot_dev_mode:{is_ur_cobot_dev_mode}"
                         "\nis_robotiq_gripper_dev_mode:{is_robotiq_gripper_dev_mode}"
                         .format(is_ur_cobot_dev_mode=is_ur_cobot_dev_mode,
                                 is_robotiq_gripper_dev_mode=is_robotiq_gripper_dev_mode))
        else:
            title = pyfiglet.figlet_format("local iothub cli", width=200)
            mode = pyfiglet.figlet_format("production mode", width=200)
            logging.info("\n{title}\n{mode}".format(title=title, mode=mode))
