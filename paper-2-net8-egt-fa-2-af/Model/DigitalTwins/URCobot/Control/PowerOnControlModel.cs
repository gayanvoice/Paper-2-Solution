using FunctionApp.Model.DigitalTwins.Shared;
using FunctionApp.Model.InternetOfThings;
using System.Diagnostics;

namespace FunctionApp.Model.URCobot.Control
{
    public class PowerOnControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static PowerOnControlModel GetControlModel(ResponseModel responseModel)
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;

            ResponsePayloadModel responsePayloadModel = new ResponsePayloadModel();
            responsePayloadModel.Status = responseModel.Payload.Status;
            responsePayloadModel.Message = responseModel.Payload.Message;
            responsePayloadModel.ElapsedTime = responseModel.Payload.Duration;

            PowerOnControlModel powerOnControlModel = new PowerOnControlModel();
            powerOnControlModel.RequestPayload = RequestPayloadModel;
            powerOnControlModel.ResponsePayload = responsePayloadModel;
            return powerOnControlModel;
        }
    }
}