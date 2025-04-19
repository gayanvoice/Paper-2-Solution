using Azure;
using Microsoft.Extensions.Logging;

namespace FunctionApp.Model.Sensor
{
    public class IlluminanceSensorModel : GOMModel
    {
        public IlluminanceSensorModel(double value): base(value)
        {
        }
        public static double MilliVoltsToLux(double milliVolts)
        {
            return milliVolts / 10.0;
        }

        public static double MilliVoltsToVolts(double milliVolts)
        {
            return milliVolts / 1000.0;
        }

        public static double LuxToMilliVolts(double lux)
        {
            return lux;
        }

        public static double VoltsToMilliVolts(double volts)
        {
            return volts * 1000.0;
        }      
        public JsonPatchDocument GetJsonPatchDocument(ILogger log)
        {
            JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
            log.LogInformation($"/var_lux {MilliVoltsToLux(VoltsToMilliVolts(Value))}");
            azureJsonPatchDocument.AppendAdd("/var_lux", MilliVoltsToLux(VoltsToMilliVolts(Value)));
            return azureJsonPatchDocument;
        }
    }
}