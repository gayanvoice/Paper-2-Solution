namespace FunctionApp.Model.URCobot.Control
{
    public class PowerOnControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static PowerOnControlModel GetPowerOnControlModel()
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;
            PowerOnControlModel powerOnControlModel = new PowerOnControlModel();
            powerOnControlModel.RequestPayload = RequestPayloadModel;
            return powerOnControlModel;
        }
    }
}