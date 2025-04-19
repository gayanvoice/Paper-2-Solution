namespace FunctionApp.Model.URCobot.Control
{
    public class UnlockProtectiveStopControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static UnlockProtectiveStopControlModel GetUnlockProtectiveStopControlModel()
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;
            UnlockProtectiveStopControlModel unlockProtectiveStopControlModel = new UnlockProtectiveStopControlModel();
            unlockProtectiveStopControlModel.RequestPayload = RequestPayloadModel;
            return unlockProtectiveStopControlModel;
        }
    }
}