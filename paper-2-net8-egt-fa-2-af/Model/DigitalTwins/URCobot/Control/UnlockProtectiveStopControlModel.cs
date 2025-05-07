using FunctionApp.Model.DigitalTwins.Shared;
using FunctionApp.Model.InternetOfThings;
using System.Diagnostics;

namespace FunctionApp.Model.URCobot.Control
{
    public class UnlockProtectiveStopControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static UnlockProtectiveStopControlModel GetControlModel(ResponseModel responseModel)
        {
            RequestPayloadModel requestPayloadModel = new RequestPayloadModel();
            requestPayloadModel.IsCommandRequested = false;

            ResponsePayloadModel responsePayloadModel = new ResponsePayloadModel();
            responsePayloadModel.Status = responseModel.Payload.Status;
            responsePayloadModel.Message = responseModel.Payload.Message;
            responsePayloadModel.ElapsedTime = responseModel.Payload.Duration;

            UnlockProtectiveStopControlModel unlockProtectiveStopControlModel = new UnlockProtectiveStopControlModel();
            unlockProtectiveStopControlModel.RequestPayload = requestPayloadModel;
            unlockProtectiveStopControlModel.ResponsePayload = responsePayloadModel;
            return unlockProtectiveStopControlModel;
        }
    }
}