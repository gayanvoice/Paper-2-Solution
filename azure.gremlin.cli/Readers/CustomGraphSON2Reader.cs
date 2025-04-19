using Gremlin.Net.Structure.IO.GraphSON;
using System.Text.Json;

namespace azure.gremlin.cli.Readers
{
    public class CustomGraphSON2Reader : GraphSON2Reader
    {
        public override dynamic? ToObject(JsonElement graphSon) =>
            graphSon.ValueKind switch
            {
                JsonValueKind.Number when graphSon.TryGetInt32(out var intValue) => intValue,
                JsonValueKind.Number when graphSon.TryGetInt64(out var longValue) => longValue,
                JsonValueKind.Number when graphSon.TryGetDecimal(out var decimalValue) => decimalValue,
                _ => base.ToObject(graphSon)
            };
    }
}