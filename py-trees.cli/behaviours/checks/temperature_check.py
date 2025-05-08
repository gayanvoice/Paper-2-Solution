import random
import typing

import py_trees


class TemperatureCheck(py_trees.behaviour.Behaviour):
    def __init__(self, condition: str, required_temperature: float, recorded_temperature: float, name: str = "Temperature Check") -> None:
        super(TemperatureCheck, self).__init__(name)
        self.condition = condition
        self.required_temperature = required_temperature
        self.recorded_temperature = recorded_temperature
        self.name = name

    def setup(self, **kwargs: typing.Any) -> None:
        self.logger.debug(f"  %s [{self.name}::setup()]" % self.name)

    def initialise(self) -> None:
        self.logger.debug(f"  %s [{self.name}::initialise()]" % self.name)

    def update(self) -> py_trees.common.Status:
        self.logger.debug(f"  %s [{self.name}::update()]" % self.name)

        conditions = {
            "equal_to": self.equal_to,
            "greater_than": self.greater_than,
            "less_than": self.less_than
        }

        return conditions.get(self.condition, lambda: py_trees.common.Status.FAILURE)()

    def terminate(self, new_status: py_trees.common.Status) -> None:
        self.logger.debug(f"  %s [{self.name}::terminate().terminate()][%s->%s]" % (self.name, self.status, new_status))

    def equal_to(self):
        if self.recorded_temperature == self.required_temperature:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

    def greater_than(self):
        if self.recorded_temperature > self.required_temperature:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

    def less_than(self):
        if self.recorded_temperature < self.required_temperature:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE
