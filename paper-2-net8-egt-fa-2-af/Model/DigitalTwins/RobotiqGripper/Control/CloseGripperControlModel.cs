using FunctionApp.Model.InternetOfThings;
using System.Diagnostics;
using FunctionApp.Model.DigitalTwins.Shared;

namespace FunctionApp.Model.DigitalTwins.RobotiqGripper.Control
{
    public class CloseGripperControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static CloseGripperControlModel GetControlModel(ResponseModel responseModel, Stopwatch stopwatch)
        {
            RequestPayloadModel requestPayloadModel = new RequestPayloadModel();
            requestPayloadModel.IsCommandRequested = false;
            ResponsePayloadModel responsePayloadModel = new ResponsePayloadModel();
            responsePayloadModel.Status = responseModel.Payload.Status;
            responsePayloadModel.Message = responseModel.Payload.Message;
            responsePayloadModel.ElapsedTime = responseModel.Payload.Duration + stopwatch.ElapsedMilliseconds;
            CloseGripperControlModel closeGripperControlModel = new CloseGripperControlModel();
            closeGripperControlModel.RequestPayload = requestPayloadModel;
            closeGripperControlModel.ResponsePayload = responsePayloadModel;
            return closeGripperControlModel;
        }
    }
}