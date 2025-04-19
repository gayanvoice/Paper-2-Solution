namespace FunctionApp.Model.URCobot
{
    public class URCobotModel
    {
        public double Value { get; private set; }

        public URCobotModel(double value)
        {
            Value = value;
        }
    }
}