from Sensor.analog_sensor import AnalogSensor


class IlluminanceSensor(AnalogSensor):
    def __init__(self, name, label, output, value):
        super().__init__(name, output, value)
        self.label = label
        if not isinstance(value, float):
            raise ValueError("Value must be a numeric float.")

    @staticmethod
    def milli_volts_to_lux(milli_volts):
        return milli_volts

    @staticmethod
    def milli_volts_to_volts(milli_volts):
        return milli_volts / 1000.0

    @staticmethod
    def lux_to_milli_volts(lux):
        return lux

    @staticmethod
    def volts_to_milli_volts(volts):
        return volts * 100.0
