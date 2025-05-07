using FunctionApp.Model.InternetOfThings;
using System.Diagnostics;
using FunctionApp.Model.DigitalTwins.Shared;

namespace FunctionApp.Model.DigitalTwins.RobotiqGripper.Control
{
    public class OpenGripperControlModel : ControlModel
    {
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static OpenGripperControlModel GetControlModel(ResponseModel responseModel, Stopwatch stopwatch)
        {
            RequestPayloadModel requestPayloadModel = new RequestPayloadModel();
            requestPayloadModel.IsCommandRequested = false;
            ResponsePayloadModel responsePayloadModel = new ResponsePayloadModel();
            responsePayloadModel.Status = responseModel.Payload.Status;
            responsePayloadModel.Message = responseModel.Payload.Message;
            responsePayloadModel.ElapsedTime = responseModel.Payload.Duration + stopwatch.ElapsedMilliseconds;
            OpenGripperControlModel openGripperControlModel = new OpenGripperControlModel();
            openGripperControlModel.RequestPayload = requestPayloadModel;
            openGripperControlModel.ResponsePayload = responsePayloadModel;
            return openGripperControlModel;
        }
    }
}