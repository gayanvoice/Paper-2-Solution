namespace FunctionApp.Model.Sensor
{
    public class GOMModel
    {
        public double Value { get; private set; }

        public GOMModel(double value)
        {
            Value = value;
        }
    }
}