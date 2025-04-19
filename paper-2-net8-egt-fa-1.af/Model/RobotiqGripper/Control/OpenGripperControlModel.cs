namespace FunctionApp.Model.RobotiqGripper.Control
{
    public class OpenGripperControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static OpenGripperControlModel GetOpenGripperControlModel()
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;
            OpenGripperControlModel openGripperControlModel = new OpenGripperControlModel();
            openGripperControlModel.RequestPayload = RequestPayloadModel;
            return openGripperControlModel;
        }
    }
}