using Newtonsoft.Json;

namespace azure.gremlin.cli.Models.ResultSet
{
    public class EdgeResultElement : IResultElement
    {
        public string? Id { get; set; }
        public string? Label { get; set; }
        public string? Type { get; set; }
        public string? InVLabel { get; set; }
        public string? OutVLabel { get; set; }
        public string? InV { get; set; }
        public string? OutV { get; set; }
        public string GetLlmInput()
        {
            if (OutV is not null &&
                Label is not null &&
                InV is not null)
            {
                Dictionary<string, object> keyPropertyDictionary = new Dictionary<string, object>();
                keyPropertyDictionary["From"] = OutV;
                keyPropertyDictionary["Relationship"] = Label;
                keyPropertyDictionary["To"] = InV;
                return JsonConvert.SerializeObject(keyPropertyDictionary, Formatting.Indented);
            }
            else
            {
                return $"Edge {Label} is not valid";
            }
        }
    }
}