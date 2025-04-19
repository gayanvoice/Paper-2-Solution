using Newtonsoft.Json.Linq;
using Newtonsoft.Json;

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
        public static MoveJControlModel GetMoveJControlModel(JToken jToken)
        {
            RequestPayloadModel RequestPayloadModel = new RequestPayloadModel();
            RequestPayloadModel.IsCommandRequested = false;
            List<double>? positionList = JsonConvert.DeserializeObject<List<double>>(jToken.ToString());
            MoveJControlModel movejControlModel = new MoveJControlModel();
            movejControlModel.Base = RadiansToDegrees(radians: Convert.ToDouble(positionList[0]));
            movejControlModel.Shoulder = RadiansToDegrees(radians: Convert.ToDouble(positionList[1]));
            movejControlModel.Elbow = RadiansToDegrees(radians: Convert.ToDouble(positionList[2]));
            movejControlModel.Wrist1 = RadiansToDegrees(radians: Convert.ToDouble(positionList[3]));
            movejControlModel.Wrist2 = RadiansToDegrees(radians: Convert.ToDouble(positionList[4]));
            movejControlModel.Wrist3 = RadiansToDegrees(radians: Convert.ToDouble(positionList[5]));
            movejControlModel.RequestPayload = RequestPayloadModel;
            return movejControlModel;
        }
        static double RadiansToDegrees(double radians)
        {
            return radians * 180.0 / Math.PI;
        }
    }
}