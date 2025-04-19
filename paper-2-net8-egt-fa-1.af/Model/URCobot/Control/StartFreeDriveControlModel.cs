namespace FunctionApp.Model.URCobot.Control
{
    public class StartFreeDriveControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static StartFreeDriveControlModel GetStartFreeDriveControlModel()
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;
            StartFreeDriveControlModel startFreeDriveControlModel = new StartFreeDriveControlModel();
            startFreeDriveControlModel.RequestPayload = RequestPayloadModel;
            return startFreeDriveControlModel;
        }
    }
}