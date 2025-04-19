import pyfiglet
import logging


class UIController:
    @staticmethod
    def welcome():
        title = pyfiglet.figlet_format("Local Simulation CLI", width=400)
        logging.info("\n{title}".format(title=title))
