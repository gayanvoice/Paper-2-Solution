using Azure;
using Microsoft.Extensions.Logging;

namespace FunctionApp.Model.Sensor
{
    public class InfraredSensorModel : DigitalSensorModel
    {
        public InfraredSensorModel(bool value): base(value)
        {
        }
        public JsonPatchDocument GetJsonPatchDocument(ILogger log)
        {
            JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
            log.LogInformation($"/var_detect_object {Value}");
            azureJsonPatchDocument.AppendAdd("/var_detect_object", Value);
            return azureJsonPatchDocument;
        }
    }
}