using FunctionApp.Model.DigitalTwins.Shared;
using FunctionApp.Model.InternetOfThings;
using System.Diagnostics;

namespace FunctionApp.Model.URCobot.Control
{
    public class MoveJControlModel : ControlModel
    {
        public double Base { get; set; }
        public double Shoulder { get; set; }
        public double Elbow { get; set; }
        public double Wrist1 { get; set; }
        public double Wrist2 { get; set; }
        public double Wrist3 { get; set; }
        public RequestPayloadModel? RequestPayload { get; set; }
        public ResponsePayloadModel? ResponsePayload { get; set; }
        public static MoveJControlModel GetControlModel(JointPositionModel jointPositionModel, ResponseModel responseModel)
        {
            RequestPayloadModel requestPayloadModel = new RequestPayloadModel();
            requestPayloadModel.IsCommandRequested = false;

            ResponsePayloadModel responsePayloadModel = new ResponsePayloadModel();
            responsePayloadModel.Status = responseModel.Payload.Status;
            responsePayloadModel.Message = responseModel.Payload.Message;
            responsePayloadModel.ElapsedTime = responseModel.Payload.Duration;

            MoveJControlModel movejControlModel = new MoveJControlModel();
            movejControlModel.Base = jointPositionModel.Base;
            movejControlModel.Shoulder = jointPositionModel.Shoulder;
            movejControlModel.Elbow = jointPositionModel.Elbow;
            movejControlModel.Wrist1 = jointPositionModel.Wrist1;
            movejControlModel.Wrist2 = jointPositionModel.Wrist2;
            movejControlModel.Wrist3 = jointPositionModel.Wrist3;
            movejControlModel.RequestPayload = requestPayloadModel;
            movejControlModel.ResponsePayload = responsePayloadModel;
            return movejControlModel;
        }
    }
}