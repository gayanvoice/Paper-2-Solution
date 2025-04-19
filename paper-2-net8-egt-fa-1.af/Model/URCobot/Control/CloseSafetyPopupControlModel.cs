namespace FunctionApp.Model.URCobot.Control
{
    public class CloseSafetyPopupControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static CloseSafetyPopupControlModel GetCloseSafetyPopupControlModel()
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;
            CloseSafetyPopupControlModel closeSafetyPopupControlModel = new CloseSafetyPopupControlModel();
            closeSafetyPopupControlModel.RequestPayload = RequestPayloadModel;
            return closeSafetyPopupControlModel;
        }
    }
}