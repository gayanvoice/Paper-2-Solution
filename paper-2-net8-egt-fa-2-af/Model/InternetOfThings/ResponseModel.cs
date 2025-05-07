using Microsoft.Azure.Devices;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace FunctionApp.Model.InternetOfThings
{
    public class ResponseModel
    {
        public int Status { get; set; }
        public PayloadModel? Payload { get; set; }
        public static ResponseModel GetSuccessResponse(CloudToDeviceMethodResult cloudToDeviceMethodResult)
        {
            string cloudToDeviceMethodResultString = JsonConvert.SerializeObject(cloudToDeviceMethodResult);
            JObject cloudToDeviceMethodResultJObject = JObject.Parse(cloudToDeviceMethodResultString);

            string payloadString = cloudToDeviceMethodResultJObject["payload"].ToString();
            JObject payloadJObject = JObject.Parse(JsonConvert.DeserializeObject<string>(payloadString));

            PayloadModel payloadModel = new PayloadModel();
            payloadModel.Status = payloadJObject["status"].Value<bool>();
            payloadModel.Duration = payloadJObject["duration"].Value<double>();
            payloadModel.Message = payloadJObject["message"].Value<string>();

            ResponseModel responseModel = new ResponseModel();
            responseModel.Status = cloudToDeviceMethodResultJObject["status"].Value<int>();
            responseModel.Payload = payloadModel;

            return responseModel;
        }
        public static ResponseModel GetExceptionResponse(string ex)
        {
            ErrorMessageModel? errorMessageModel = JsonConvert.DeserializeObject<ErrorMessageModel>(ex);

            PayloadModel payloadModel = new PayloadModel();
            payloadModel.Status = false;
            if (errorMessageModel is not null && errorMessageModel.Error is not null)
            {
                payloadModel.Message = errorMessageModel.Error.Message;
            }
            else
            {
                payloadModel.Message = "No Error Message";
            }

            ResponseModel responseModel = new ResponseModel();
            responseModel.Status = 500;
            responseModel.Payload = payloadModel;
            return responseModel;
        }
        public class PayloadModel
        {
            public bool Status { get; set; }
            public double Duration { get; set; }
            public string? Message { get; set; }
        }
    }
}