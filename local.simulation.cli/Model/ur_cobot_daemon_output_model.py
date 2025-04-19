class URCobotDaemonOutputModel:
    def __init__(
            self,
            standard_analog_out_0=None,
            standard_analog_out_1=None,
            standard_digital_out_0=None,
            standard_digital_out_1=None,
            standard_digital_out_2=None,
            standard_digital_out_3=None,
            standard_digital_out_4=None,
            standard_digital_out_5=None,
            standard_digital_out_6=None,
            standard_digital_out_7=None):
        if (standard_analog_out_0 is not None and
                standard_analog_out_1 is not None and
                standard_digital_out_0 is not None and
                standard_digital_out_1 is not None and
                standard_digital_out_2 is not None and
                standard_digital_out_3 is not None and
                standard_digital_out_4 is not None and
                standard_digital_out_5 is not None and
                standard_digital_out_6 is not None and
                standard_digital_out_7 is not None):
            self._standard_analog_out_0 = standard_analog_out_0
            self._standard_analog_out_1 = standard_analog_out_1
            self._standard_digital_out_0 = standard_digital_out_0
            self._standard_digital_out_1 = standard_digital_out_1
            self._standard_digital_out_2 = standard_digital_out_2
            self._standard_digital_out_3 = standard_digital_out_3
            self._standard_digital_out_4 = standard_digital_out_4
            self._standard_digital_out_5 = standard_digital_out_5
            self._standard_digital_out_6 = standard_digital_out_6
            self._standard_digital_out_7 = standard_digital_out_7
        else:
            self._standard_analog_out_0 = None
            self._standard_analog_out_1 = None
            self._standard_digital_out_0 = None
            self._standard_digital_out_1 = None
            self._standard_digital_out_2 = None
            self._standard_digital_out_3 = None
            self._standard_digital_out_4 = None
            self._standard_digital_out_5 = None
            self._standard_digital_out_6 = None
            self._standard_digital_out_7 = None

    @property
    def standard_analog_out_0(self):
        return self._standard_analog_out_0

    @property
    def standard_analog_out_1(self):
        return self._standard_analog_out_1

    @property
    def standard_digital_out_0(self):
        return self._standard_digital_out_0

    @property
    def standard_digital_out_1(self):
        return self._standard_digital_out_1

    @property
    def standard_digital_out_2(self):
        return self._standard_digital_out_2

    @property
    def standard_digital_out_3(self):
        return self._standard_digital_out_3

    @property
    def standard_digital_out_4(self):
        return self._standard_digital_out_4

    @property
    def standard_digital_out_5(self):
        return self._standard_digital_out_5

    @property
    def standard_digital_out_6(self):
        return self._standard_digital_out_6

    @property
    def standard_digital_out_7(self):
        return self._standard_digital_out_7

    @standard_analog_out_0.setter
    def standard_analog_out_0(self, value):
        if not isinstance(value, float) or value < 0:
            raise ValueError(f"'invalid value {value}'. standard_analog_out_0 must be a non-negative float.")
        self._standard_analog_out_0 = value

    @standard_analog_out_1.setter
    def standard_analog_out_1(self, value):
        if not isinstance(value, float) or value < 0:
            raise ValueError(f"'invalid value {value}'. standard_analog_out_1 must be a non-negative float.")
        self._standard_analog_out_1 = value

    @standard_digital_out_0.setter
    def standard_digital_out_0(self, value):
        if not isinstance(value, int) or value < 0 or value > 1:
            raise ValueError(f"'invalid value {value}'. standard_digital_out_0 must be a non-negative integer 1 or 0.")
        self._standard_digital_out_0 = value

    @standard_digital_out_1.setter
    def standard_digital_out_1(self, value):
        if not isinstance(value, int) or value < 0 or value > 1:
            raise ValueError(f"'invalid value {value}'. standard_digital_out_1 must be a non-negative integer 1 or 0.")
        self._standard_digital_out_1 = value

    @standard_digital_out_2.setter
    def standard_digital_out_2(self, value):
        if not isinstance(value, int) or value < 0 or value > 1:
            raise ValueError(f"'invalid value {value}'. standard_digital_out_2 must be a non-negative integer 1 or 0.")
        self._standard_digital_out_2 = value

    @standard_digital_out_3.setter
    def standard_digital_out_3(self, value):
        if not isinstance(value, int) or value < 0 or value > 1:
            raise ValueError(f"'invalid value {value}'. standard_digital_out_3 must be a non-negative integer 1 or 0.")
        self._standard_digital_out_3 = value

    @standard_digital_out_4.setter
    def standard_digital_out_4(self, value):
        if not isinstance(value, int) or value < 0 or value > 1:
            raise ValueError(f"'invalid value {value}'. standard_digital_out_4 must be a non-negative integer 1 or 0.")
        self._standard_digital_out_4 = value

    @standard_digital_out_5.setter
    def standard_digital_out_5(self, value):
        if not isinstance(value, int) or value < 0 or value > 1:
            raise ValueError(f"'invalid value {value}'. standard_digital_out_5 must be a non-negative integer 1 or 0.")
        self._standard_digital_out_5 = value

    @standard_digital_out_6.setter
    def standard_digital_out_6(self, value):
        if not isinstance(value, int) or value < 0 or value > 1:
            raise ValueError(f"'invalid value {value}'. standard_digital_out_6 must be a non-negative integer 1 or 0.")
        self._standard_digital_out_6 = value

    @standard_digital_out_7.setter
    def standard_digital_out_7(self, value):
        if not isinstance(value, int) or value < 0 or value > 1:
            raise ValueError(f"'invalid value {value}'. standard_digital_out_7 must be a non-negative integer 1 or 0.")
        self._standard_digital_out_7 = value
