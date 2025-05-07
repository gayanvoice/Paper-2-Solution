using FunctionApp.Model.InternetOfThings;
using System.Diagnostics;
using FunctionApp.Model.DigitalTwins.Shared;

namespace FunctionApp.Model.DigitalTwins.RobotiqGripper.Control
{
    public class ActivateGripperControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static ActivateGripperControlModel GetControlModel(ResponseModel responseModel, Stopwatch stopwatch)
        {
            RequestPayloadModel requestPayloadModel = new RequestPayloadModel();
            requestPayloadModel.IsCommandRequested = false;
            ResponsePayloadModel responsePayloadModel = new ResponsePayloadModel();
            responsePayloadModel.Status = responseModel.Payload.Status;
            responsePayloadModel.Message = responseModel.Payload.Message;
            responsePayloadModel.ElapsedTime = responseModel.Payload.Duration + stopwatch.ElapsedMilliseconds;  
            ActivateGripperControlModel activateGripperControlModel = new ActivateGripperControlModel();
            activateGripperControlModel.RequestPayload = requestPayloadModel;
            activateGripperControlModel.ResponsePayload = responsePayloadModel;
            return activateGripperControlModel;
        }
    }
}