namespace FunctionApp.Model.URCobot.Control
{
    public class ClosePopupControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static ClosePopupControlModel GetClosePopupControlModel()
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;
            ClosePopupControlModel closePopupControlModel = new ClosePopupControlModel();
            closePopupControlModel.RequestPayload = RequestPayloadModel;
            return closePopupControlModel;
        }
    }
}