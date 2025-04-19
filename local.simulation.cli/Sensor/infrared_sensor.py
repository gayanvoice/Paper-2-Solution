from Sensor.digital_sensor import DigitalSensor


class InfraredSensor(DigitalSensor):
    def __init__(self, name, label, output, value):
        super().__init__(name, output, value)
        self.label = label
        if not isinstance(value, int):
            raise ValueError("Value must be a numeric integer.")
