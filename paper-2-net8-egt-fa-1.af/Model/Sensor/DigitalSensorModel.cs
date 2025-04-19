namespace FunctionApp.Model.Sensor
{
    public class DigitalSensorModel
    {
        public bool Value { get; private set; }

        public DigitalSensorModel(bool value)
        {
            Value = value;
        }
    }
}