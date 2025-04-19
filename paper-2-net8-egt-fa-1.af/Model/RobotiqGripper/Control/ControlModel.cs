namespace FunctionApp.Model.RobotiqGripper.Control
{
    public class ControlModel
    {
        public class RequestPayloadModel
        {
            public bool IsCommandRequested { get; set; }
        }
        public class ResponsePayloadModel
        {
            public bool Status { get; set; }
            public string Message { get; set; }
            public double ElapsedTime { get; set; }
        }
    }
}