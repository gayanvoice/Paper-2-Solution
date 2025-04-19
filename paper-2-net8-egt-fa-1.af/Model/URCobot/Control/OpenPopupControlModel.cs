namespace FunctionApp.Model.URCobot.Control
{
    public class OpenPopupControlModel : ControlModel
    {
        public string? PopupText { get; set; }
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static OpenPopupControlModel GetOpenPopupControlModel()
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;
            OpenPopupControlModel openPopupControlModel = new OpenPopupControlModel();
            openPopupControlModel.PopupText = "null";
            openPopupControlModel.RequestPayload = RequestPayloadModel;
            return openPopupControlModel;
        }
    }
}