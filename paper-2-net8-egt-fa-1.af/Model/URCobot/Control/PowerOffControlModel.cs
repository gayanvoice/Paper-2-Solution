namespace FunctionApp.Model.URCobot.Control
{
    public class PowerOffControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static PowerOffControlModel GetPowerOffControlModel()
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;
            PowerOffControlModel powerOffControlModel = new PowerOffControlModel();
            powerOffControlModel.RequestPayload = RequestPayloadModel;
            return powerOffControlModel;
        }
    }
}