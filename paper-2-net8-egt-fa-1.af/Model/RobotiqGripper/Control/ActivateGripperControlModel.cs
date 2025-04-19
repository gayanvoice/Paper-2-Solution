namespace FunctionApp.Model.RobotiqGripper.Control
{
    public class ActivateGripperControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static ActivateGripperControlModel GetActivateGripperControlModel()
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;
            ActivateGripperControlModel activateGripperControlModel = new ActivateGripperControlModel();
            activateGripperControlModel.RequestPayload = RequestPayloadModel;
            return activateGripperControlModel;
        }
    }
}