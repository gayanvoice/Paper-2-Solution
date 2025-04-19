namespace FunctionApp.Model.RobotiqGripper.Control
{
    public class CloseGripperControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static CloseGripperControlModel GetCloseGripperControlModel()
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;
            CloseGripperControlModel closeGripperControlModel = new CloseGripperControlModel();
            closeGripperControlModel.RequestPayload = RequestPayloadModel;
            return closeGripperControlModel;
        }
    }
}