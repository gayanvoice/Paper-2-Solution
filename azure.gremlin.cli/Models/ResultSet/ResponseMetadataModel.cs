using azure.gremlin.cli.Helpers;
using Gremlin.Net.Driver;
using Newtonsoft.Json;

namespace azure.gremlin.cli.Models.ResultSet
{
    public class ResponseMetadataModel
    {
        [JsonProperty("x-ms-status-code")]
        public int StatusCode { get; set; }

        [JsonProperty("x-ms-activity-id")]
        public string? ActivityId { get; set; }

        [JsonProperty("x-ms-request-charge")]
        public double RequestCharge { get; set; }

        [JsonProperty("x-ms-total-request-charge")]
        public double TotalRequestCharge { get; set; }

        [JsonProperty("x-ms-server-time-ms")]
        public double ServerTimeMs { get; set; }

        [JsonProperty("x-ms-total-server-time-ms")]
        public double TotalServerTimeMs { get; set; }
        public static ResponseMetadataModel Create(ResultSet<dynamic> resultSet)
        {
            object? statusCode = ParseHelper.GetValueOrDefault(resultSet.StatusAttributes, "x-ms-status-code");
            object? activityId = ParseHelper.GetValueOrDefault(resultSet.StatusAttributes, "x-ms-activity-id");
            object? requestCharge = ParseHelper.GetValueOrDefault(resultSet.StatusAttributes, "x-ms-request-charge");
            object? totalRequestCharge = ParseHelper.GetValueOrDefault(resultSet.StatusAttributes, "x-ms-total-request-charge");
            object? serverTimeMs = ParseHelper.GetValueOrDefault(resultSet.StatusAttributes, "x-ms-server-time-ms");
            object? totalServerTimeMs = ParseHelper.GetValueOrDefault(resultSet.StatusAttributes, "x-ms-total-server-time-ms");

            ResponseMetadataModel cosmosDbResponseMetadataModel = new ResponseMetadataModel();

            if (statusCode is not null) cosmosDbResponseMetadataModel.StatusCode = (int)statusCode;
            else cosmosDbResponseMetadataModel.StatusCode = 0;

            if (activityId is not null) cosmosDbResponseMetadataModel.ActivityId = activityId.ToString();
            else cosmosDbResponseMetadataModel.ActivityId = default;

            if (requestCharge is not null) cosmosDbResponseMetadataModel.RequestCharge = (double)requestCharge;
            else cosmosDbResponseMetadataModel.RequestCharge = 0.0;

            if (totalRequestCharge is not null) cosmosDbResponseMetadataModel.TotalRequestCharge = (double)totalRequestCharge;
            else cosmosDbResponseMetadataModel.TotalRequestCharge = 0.0;

            if (serverTimeMs is not null) cosmosDbResponseMetadataModel.ServerTimeMs = (double)serverTimeMs;
            else cosmosDbResponseMetadataModel.ServerTimeMs = 0.0;

            if (totalServerTimeMs is not null) cosmosDbResponseMetadataModel.TotalServerTimeMs = (double)totalServerTimeMs;
            else cosmosDbResponseMetadataModel.TotalServerTimeMs = 0.0;

            return cosmosDbResponseMetadataModel;
        }
    }
}