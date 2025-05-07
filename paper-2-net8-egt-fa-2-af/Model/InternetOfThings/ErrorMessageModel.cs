using Newtonsoft.Json;

namespace FunctionApp.Model.InternetOfThings
{
    public class ErrorMessageModel
    {
        [JsonProperty("Message")]
        public string? MessageJson { get; set; }
        public string? ExceptionMessage { get; set; }
        [JsonIgnore]
        public ErrorModel? Error
        {
            get
            {
                return JsonConvert.DeserializeObject<ErrorModel>(MessageJson);
            }
        }
        public class Info
        {
            public string? Timeout { get; set; }
        }
        public class ErrorModel
        {
            public int ErrorCode { get; set; }
            public string? TrackingId { get; set; }
            public string? Message { get; set; }
            public Info? Info { get; set; }
            public string? TimestampUtc { get; set; }
        }
    }
}