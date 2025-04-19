class AnalogSensor:
    def __init__(self, name, output, value):
        self.name = name
        self.output = output
        if isinstance(value, float):
            self.value = value
        else:
            raise ValueError("Value must be a numeric float.")
