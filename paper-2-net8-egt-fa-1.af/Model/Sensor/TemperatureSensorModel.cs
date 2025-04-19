using Azure;
using Microsoft.Extensions.Logging;

namespace FunctionApp.Model.Sensor
{
    public class TemperatureSensorModel : GOMModel
    {
        public TemperatureSensorModel(double value): base(value)
        {
        }
        public static double MilliVoltsToCelsius(double milliVolts)
        {
            return milliVolts / 100.0;
        }

        public static double MilliVoltsToVolts(double milliVolts)
        {
            return milliVolts / 1000.0;
        }

        public static double CelsiusToMilliVolts(double celsius)
        {
            return celsius * 10.0;
        }

        public static double VoltsToMilliVolts(double volts)
        {
            return volts * 1000.0;
        }
        public JsonPatchDocument GetJsonPatchDocument(ILogger log)
        {
            JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
            log.LogInformation($"/var_degree_celsius {MilliVoltsToCelsius(VoltsToMilliVolts(Value))}");
            azureJsonPatchDocument.AppendAdd("/var_degree_celsius", MilliVoltsToCelsius(VoltsToMilliVolts(Value)));
            return azureJsonPatchDocument;
        }
    }
}