namespace FunctionApp.Model.URCobot.Control
{
    public class StopFreeDriveControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static StopFreeDriveControlModel GetStopFreeDriveControlModel()
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;
            StopFreeDriveControlModel stopFreeDriveControlModel = new StopFreeDriveControlModel();
            stopFreeDriveControlModel.RequestPayload = RequestPayloadModel;
            return stopFreeDriveControlModel;
        }
    }
}