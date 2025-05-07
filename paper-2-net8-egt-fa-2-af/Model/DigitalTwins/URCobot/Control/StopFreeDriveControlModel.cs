using FunctionApp.Model.DigitalTwins.Shared;
using FunctionApp.Model.InternetOfThings;
using System.Diagnostics;

namespace FunctionApp.Model.URCobot.Control
{
    public class StopFreeDriveControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static StopFreeDriveControlModel GetControlModel(ResponseModel responseModel)
        {
            RequestPayloadModel requestPayloadModel = new RequestPayloadModel();
            requestPayloadModel.IsCommandRequested = false;

            ResponsePayloadModel responsePayloadModel = new ResponsePayloadModel();
            responsePayloadModel.Status = responseModel.Payload.Status;
            responsePayloadModel.Message = responseModel.Payload.Message;
            responsePayloadModel.ElapsedTime = responseModel.Payload.Duration;

            StopFreeDriveControlModel stopFreeDriveControlModel = new StopFreeDriveControlModel();
            stopFreeDriveControlModel.RequestPayload = requestPayloadModel;
            stopFreeDriveControlModel.ResponsePayload = responsePayloadModel;
            return stopFreeDriveControlModel;
        }
    }
}