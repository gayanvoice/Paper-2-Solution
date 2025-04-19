# -*- coding: cp1252 -*-

import asyncio
import cmd
import logging
import time
import random

from typing import Dict, Tuple
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from Controller.ui_controller import UIController
from Controller.ur_cobot_daemon_controller import URCobotDaemonController
from Controller.primary_client_controller import PrimaryClientController
from Sensor.analog_sensor import AnalogSensor
from Sensor.digital_sensor import DigitalSensor
from Sensor.illuminance_sensor import IlluminanceSensor
from Sensor.infrared_sensor import InfraredSensor
from Sensor.temperature_sensor import TemperatureSensor
from rich.prompt import Prompt, FloatPrompt, IntPrompt, Confirm
from rich.table import Column, Table
from Wrapper.execute_with_timing_wrapper import execute_with_timing_wrapper

logging.basicConfig(filename='local-simulation-cli-log.log', filemode='w', level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(name)s  - %(message)s")


class LocalSimulationCli(cmd.Cmd):
    intro = "Welcome to the Local Simulation CLI. Type help or ? to list commands.\n"
    prompt = "(Local-Simulation-CLI) "

    @execute_with_timing_wrapper
    def __init__(self):
        super().__init__()
        ui_controller = UIController()
        ui_controller.welcome()
        self.hostname = '192.168.1.134'
        self.primary_client_port = 30002
        self.ur_cobot_daemon_controller = URCobotDaemonController()
        self.primary_client_controller = PrimaryClientController()

        self.console = Console()
        self.sensors = {
            "t1": TemperatureSensor(name="temperature_sensor_1", label="temperature_1", output=0, value=0.0),
            "l1": IlluminanceSensor(name="illuminance_sensor_1", label="light_1", output=1, value=0.0),
            "up1": InfraredSensor(name="infrared_sensor_1", label="unloading_position_1", output=0, value=0),
            "up2": InfraredSensor(name="infrared_sensor_2", label="unloading_position_2", output=1, value=0),
            "lp1": InfraredSensor(name="infrared_sensor_3", label="loading_position_1", output=2, value=0),
            "lp2": InfraredSensor(name="infrared_sensor_4", label="loading_position_2", output=3, value=0)
        }

    @execute_with_timing_wrapper
    def do_connect(self, arg):
        """Connect to the Universal Robots Simulation environment: connect"""
        if self.primary_client_controller.is_connected():
            self.console.print(
                f"already connected to the primary client at {self.hostname}:{str(self.primary_client_port)}.",
                style="yellow")
            logging.info(f"already connected to the primary client at {self.hostname}:{str(self.primary_client_port)}.")
        else:
            try:
                self.primary_client_controller.connect(hostname=self.hostname, port=self.primary_client_port)
                self.console.print(
                    f"successfully connected to the primary client at {self.hostname}:{str(self.primary_client_port)}.",
                    style="green")
                logging.info(
                    f"successfully connected to the primary client at {self.hostname}:{str(self.primary_client_port)}.")
            except ConnectionRefusedError:
                self.console.print(
                    f"could not connect to the primary client at {self.hostname}:{str(self.primary_client_port)}. "
                    f"it is possible your universal robots simulation is not running. please check the status of the simulation.",
                    style="red")
                logging.error(
                    f"could not connect to the primary client at {self.hostname}:{str(self.primary_client_port)}. "
                    f"it is possible your universal robots simulation is not running. please check the status of the simulation.")
            except Exception:
                self.console.print(
                    f"could not connect to the primary client at {self.hostname}:{str(self.primary_client_port)}. an unknown error occurred.",
                    style="red")
                logging.error(
                    f"could not connect to the primary client at {self.hostname}:{str(self.primary_client_port)}. an unknown error occurred.")

    @execute_with_timing_wrapper
    def do_disconnect(self, arg):
        """Disconnect from the Universal Robots Simulation environment: disconnect"""
        try:
            if self.primary_client_controller.is_connected():
                self.primary_client_controller.disconnect()
                self.console.print(
                    f"successfully disconnected from the primary client at {self.hostname}:{str(self.primary_client_port)}.",
                    style="green")
                logging.info(
                    f"successfully disconnected from the primary client at {self.hostname}:{str(self.primary_client_port)}.")
            else:
                self.console.print(
                    f"already disconnected from the primary client at {self.hostname}:{str(self.primary_client_port)}.",
                    style="yellow")
                logging.info(
                    f"already disconnected from the primary client at {self.hostname}:{str(self.primary_client_port)}.")
        except AttributeError:
            self.console.print(
                f"could not disconnect from the primary client at {self.hostname}:{str(self.primary_client_port)}." +
                "it is possible you are not connected to the universal robots simulation. please check the status of the simulation.",
                style="red")
            logging.error(
                f"could not disconnect from the primary client at {self.hostname}:{str(self.primary_client_port)}." +
                "it is possible you are not connected to the universal robots simulation. please check the status of the simulation.")
        except Exception:
            self.console.print(
                f"could not disconnect from the primary client at {self.hostname}:{str(self.primary_client_port)}. an unknown error occurred.",
                style="red")
            logging.error(f"could not disconnect from the primary client at {self.hostname}:{str(self.primary_client_port)}. an unknown error occurred.")

    @execute_with_timing_wrapper
    def do_exit(self, arg):
        """Exit from the Local-Simulation-CLI: exit"""
        self.do_disconnect(arg)
        self.console.print(f"successfully exit from the local simulation cli.", style="green")
        logging.info(f"successfully exit from the local simulation cli.")
        return True

    @execute_with_timing_wrapper
    def do_quit(self, arg):
        """Exit from the Local-Simulation-CLI: quit"""
        self.do_disconnect(arg)
        self.console.print(f"successfully exit from the local simulation cli.", style="green")
        logging.info(f"successfully exit from the local simulation cli.")
        return True

    def get_panel(self, sensor_id):
        sensor = self.sensors.get(sensor_id)
        if not self.primary_client_controller.is_connected():
            self.do_connect(None)

        ur_cobot_deamon_controller_output_model = asyncio.run(
            self.ur_cobot_daemon_controller.get_ur_cobot_daemon_output_model())

        standard_digital_out_0_in_celsius = TemperatureSensor.milli_volts_to_celsius(
            TemperatureSensor.volts_to_milli_volts(ur_cobot_deamon_controller_output_model.standard_analog_out_0))
        standard_digital_out_1_in_lux = IlluminanceSensor.milli_volts_to_lux(
            IlluminanceSensor.volts_to_milli_volts(ur_cobot_deamon_controller_output_model.standard_analog_out_1))

        if issubclass(type(sensor), AnalogSensor):
            if issubclass(type(sensor), TemperatureSensor):
                return f"[b]{sensor.label}[/b]\n{sensor.name}\n[yellow]{standard_digital_out_0_in_celsius}°C"
            elif issubclass(type(sensor), IlluminanceSensor):
                return f"[b]{sensor.label}[/b]\n{sensor.name}\n[yellow]{standard_digital_out_1_in_lux} lx"
        elif issubclass(type(sensor), DigitalSensor):
            if issubclass(type(sensor), InfraredSensor):
                if sensor.name == "infrared_sensor_1":
                    return f"[b]{sensor.label}[/b]\n{sensor.name}\n[yellow]{ur_cobot_deamon_controller_output_model.standard_digital_out_0}"
                elif sensor.name == "infrared_sensor_2":
                    return f"[b]{sensor.label}[/b]\n{sensor.name}\n[yellow]{ur_cobot_deamon_controller_output_model.standard_digital_out_1}"
                elif sensor.name == "infrared_sensor_3":
                    return f"[b]{sensor.label}[/b]\n{sensor.name}\n[yellow]{ur_cobot_deamon_controller_output_model.standard_digital_out_2}"
                elif sensor.name == "infrared_sensor_4":
                    return f"[b]{sensor.label}[/b]\n{sensor.name}\n[yellow]{ur_cobot_deamon_controller_output_model.standard_digital_out_3}"

    @execute_with_timing_wrapper
    def do_show(self, arg):
        """Get values from sensors: simulation"""
        console = Console()
        sensor_panels = [Panel(self.get_panel(sensor_id=sensor_id), expand=True) for sensor_id in self.sensors.keys()]
        console.print(Columns(sensor_panels))

    @execute_with_timing_wrapper
    def do_get(self, arg):
        """Get values from sensors: get"""
        sensor = self.sensors.get(Prompt.ask("choose the sensor", choices=list(self.sensors.keys())))

        if not self.primary_client_controller.is_connected():
            self.do_connect(arg)

        ur_cobot_deamon_controller_output_model = asyncio.run(
            self.ur_cobot_daemon_controller.get_ur_cobot_daemon_output_model())
        if issubclass(type(sensor), AnalogSensor):
            if issubclass(type(sensor), TemperatureSensor):
                sensor.value = ur_cobot_deamon_controller_output_model.standard_analog_out_0
            elif issubclass(type(sensor), IlluminanceSensor):
                sensor.value = ur_cobot_deamon_controller_output_model.standard_analog_out_1
            self.console.print(f"name:[green]{sensor.name}[/green] label:[green]{sensor.label}[/green] "
                               f"type:[green]analog[/green] output:[green]{sensor.output}[/green] "
                               f"value:[green]{sensor.value}[/green]", style="none")
            logging.info(f"name:[green]{sensor.name}[/green] label:[green]{sensor.label}[/green] "
                               f"type:[green]analog[/green] output:[green]{sensor.output}[/green] "
                               f"value:[green]{sensor.value}[/green]")

        if issubclass(type(sensor), DigitalSensor):
            if issubclass(type(sensor), InfraredSensor):
                if sensor.name == "infrared_sensor_1":
                    sensor.value = ur_cobot_deamon_controller_output_model.standard_digital_out_0
                elif sensor.name == "infrared_sensor_2":
                    sensor.value = ur_cobot_deamon_controller_output_model.standard_digital_out_1
                elif sensor.name == "infrared_sensor_3":
                    sensor.value = ur_cobot_deamon_controller_output_model.standard_digital_out_2
                elif sensor.name == "infrared_sensor_4":
                    sensor.value = ur_cobot_deamon_controller_output_model.standard_digital_out_3
                self.console.print(f"name:[green]{sensor.name}[/green] label:[green]{sensor.label}[/green] "
                                   f"type:[green]digital[/green] output:[green]{sensor.output}[/green] "
                                   f"value:[green]{sensor.value}[/green]", style="none")
                logging.info(f"name:[green]{sensor.name}[/green] label:[green]{sensor.label}[/green] "
                                   f"type:[green]digital[/green] output:[green]{sensor.output}[/green] "
                                   f"value:[green]{sensor.value}[/green]")

    @execute_with_timing_wrapper
    def do_set(self, arg):
        """Set values for sensors: set"""
        sensor = self.sensors.get(Prompt.ask("choose the sensor", choices=list(self.sensors.keys())))

        if not self.primary_client_controller.is_connected():
            self.do_connect(arg)

        ur_cobot_deamon_controller_output_model = asyncio.run(
            self.ur_cobot_daemon_controller.get_ur_cobot_daemon_output_model())

        standard_digital_out_0_in_celsius = TemperatureSensor.milli_volts_to_celsius(
            TemperatureSensor.volts_to_milli_volts(ur_cobot_deamon_controller_output_model.standard_analog_out_0))
        standard_digital_out_1_in_lux = IlluminanceSensor.milli_volts_to_lux(
            IlluminanceSensor.volts_to_milli_volts(ur_cobot_deamon_controller_output_model.standard_analog_out_1))

        if issubclass(type(sensor), AnalogSensor):
            if issubclass(type(sensor), TemperatureSensor):
                input_value_in_celsius = FloatPrompt.ask(f"set celsius value for {sensor.label}",
                                                         default=f"{standard_digital_out_0_in_celsius}°C")
                input_value_in_volts = TemperatureSensor.milli_volts_to_volts(
                    TemperatureSensor.celsius_to_milli_volts(input_value_in_celsius))
                if self.primary_client_controller.send_analog_value(sensor.output, input_value_in_volts):
                    self.console.print(f"changed floating value for [green]{sensor.name}[/green] "
                                       f"from {ur_cobot_deamon_controller_output_model.standard_analog_out_0} ({standard_digital_out_0_in_celsius}°C) "
                                       f"to {input_value_in_volts} ({input_value_in_celsius}°C).")
                    logging.info(f"changed floating value for [green]{sensor.name}[/green] "
                                       f"from {ur_cobot_deamon_controller_output_model.standard_analog_out_0} ({standard_digital_out_0_in_celsius}°C) "
                                       f"to {input_value_in_volts} ({input_value_in_celsius}°C).")
                else:
                    self.console.print(
                        f"error occurred while setting for [green]{sensor.name}[/green] to {input_value_in_volts}({input_value_in_celsius}°C).")
                    logging.error(f"error occurred while setting for [green]{sensor.name}[/green] to {input_value_in_volts}({input_value_in_celsius}°C).")
            if issubclass(type(sensor), IlluminanceSensor):
                input_value_in_lx = FloatPrompt.ask(f"set lux value for {sensor.label} (recommended=200 lx)",
                                                    default=f"{standard_digital_out_1_in_lux} lx")
                input_value_in_volts = IlluminanceSensor.milli_volts_to_volts(
                    IlluminanceSensor.lux_to_milli_volts(input_value_in_lx))
                if self.primary_client_controller.send_analog_value(sensor.output, input_value_in_volts):
                    self.console.print(
                        f"changed floating value for [green]{sensor.name}[/green] "
                        f"from {ur_cobot_deamon_controller_output_model.standard_analog_out_1} ({standard_digital_out_1_in_lux} lx) "
                        f"to {input_value_in_volts} ({input_value_in_lx} lx).")
                    logging.info(f"changed floating value for [green]{sensor.name}[/green] "
                        f"from {ur_cobot_deamon_controller_output_model.standard_analog_out_1} ({standard_digital_out_1_in_lux} lx) "
                        f"to {input_value_in_volts} ({input_value_in_lx} lx).")
                else:
                    self.console.print(
                        f"error occurred while setting for [green]{sensor.name}[/green] to {input_value_in_volts}({input_value_in_lx} lx).")
                    logging.error(f"error occurred while setting for [green]{sensor.name}[/green] to {input_value_in_volts}({input_value_in_lx} lx).")

        if issubclass(type(sensor), DigitalSensor):
            if issubclass(type(sensor), InfraredSensor):
                if sensor.name == "infrared_sensor_1":
                    input_value_in_bool = Confirm.ask(f"set value true for {sensor.label}",
                                                      default=ur_cobot_deamon_controller_output_model.standard_digital_out_0)
                    if self.primary_client_controller.send_digital_value(sensor.output, input_value_in_bool):
                        self.console.print(
                            f"changed boolean value for [green]{sensor.name}[/green] "
                            f"from {ur_cobot_deamon_controller_output_model.standard_digital_out_0} to {input_value_in_bool}.")
                        logging.info(f"changed boolean value for [green]{sensor.name}[/green] "
                            f"from {ur_cobot_deamon_controller_output_model.standard_digital_out_0} to {input_value_in_bool}.")
                    else:
                        self.console.print(
                            f"error occurred while setting for [green]{sensor.name}[/green] to {input_value_in_bool} to .")
                        logging.error(f"error occurred while setting for [green]{sensor.name}[/green] to {input_value_in_bool} to .")
                elif sensor.name == "infrared_sensor_2":
                    input_value_in_bool = Confirm.ask(f"set value true for {sensor.label}",
                                                      default=ur_cobot_deamon_controller_output_model.standard_digital_out_1)
                    if self.primary_client_controller.send_digital_value(sensor.output, input_value_in_bool):
                        self.console.print(
                            f"changed boolean value for [green]{sensor.name}[/green] "
                            f"from {ur_cobot_deamon_controller_output_model.standard_digital_out_1} to {input_value_in_bool}.")
                        logging.info( f"changed boolean value for [green]{sensor.name}[/green] "
                            f"from {ur_cobot_deamon_controller_output_model.standard_digital_out_1} to {input_value_in_bool}.")
                    else:
                        self.console.print(
                            f"error occurred while setting for [green]{sensor.name}[/green] to {input_value_in_bool} to .")
                        logging.error( f"error occurred while setting for [green]{sensor.name}[/green] to {input_value_in_bool} to .")
                elif sensor.name == "infrared_sensor_3":
                    input_value_in_bool = Confirm.ask(f"set value true for {sensor.label}",
                                                      default=ur_cobot_deamon_controller_output_model.standard_digital_out_2)
                    if self.primary_client_controller.send_digital_value(sensor.output, input_value_in_bool):
                        self.console.print(
                            f"changed boolean value for [green]{sensor.name}[/green] "
                            f"from {ur_cobot_deamon_controller_output_model.standard_digital_out_2} to {input_value_in_bool}.")
                        logging.info(f"changed boolean value for [green]{sensor.name}[/green] "
                            f"from {ur_cobot_deamon_controller_output_model.standard_digital_out_2} to {input_value_in_bool}.")
                    else:
                        self.console.print(
                            f"error occurred while setting for [green]{sensor.name}[/green] to {input_value_in_bool} to .")
                        logging.error(f"error occurred while setting for [green]{sensor.name}[/green] to {input_value_in_bool} to .")
                elif sensor.name == "infrared_sensor_4":
                    input_value_in_bool = Confirm.ask(f"set value true for {sensor.label}",
                                                      default=ur_cobot_deamon_controller_output_model.standard_digital_out_3)
                    if self.primary_client_controller.send_digital_value(sensor.output, input_value_in_bool):
                        self.console.print(
                            f"changed boolean value for [green]{sensor.name}[/green] "
                            f"from {ur_cobot_deamon_controller_output_model.standard_digital_out_3} to {input_value_in_bool}.")
                        logging.info(f"changed boolean value for [green]{sensor.name}[/green] "
                            f"from {ur_cobot_deamon_controller_output_model.standard_digital_out_3} to {input_value_in_bool}.")
                    else:
                        self.console.print(
                            f"error occurred while setting for [green]{sensor.name}[/green] to {input_value_in_bool} to .")
                        logging.error(f"error occurred while setting for [green]{sensor.name}[/green] to {input_value_in_bool} to .")


if __name__ == '__main__':
    LocalSimulationCli().cmdloop()

