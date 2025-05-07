using FunctionApp.Model.DigitalTwins.Shared;
using FunctionApp.Model.InternetOfThings;
using System.Diagnostics;

namespace FunctionApp.Model.URCobot.Control
{
    public class OpenPopupControlModel : ControlModel
    {
        public string? PopupText { get; set; }
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static OpenPopupControlModel GetControlModel(ResponseModel responseModel)
        {
            RequestPayloadModel requestPayloadModel = new RequestPayloadModel();
            requestPayloadModel.IsCommandRequested = false;

            ResponsePayloadModel responsePayloadModel = new ResponsePayloadModel();
            responsePayloadModel.Status = responseModel.Payload.Status;
            responsePayloadModel.Message = responseModel.Payload.Message;
            responsePayloadModel.ElapsedTime = responseModel.Payload.Duration;

            OpenPopupControlModel openPopupControlModel = new OpenPopupControlModel();
            openPopupControlModel.PopupText = string.Empty;
            openPopupControlModel.RequestPayload = requestPayloadModel;
            openPopupControlModel.ResponsePayload = responsePayloadModel;
            return openPopupControlModel;
        }
    }
}