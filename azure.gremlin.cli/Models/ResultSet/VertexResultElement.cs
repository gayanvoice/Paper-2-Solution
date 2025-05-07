using Newtonsoft.Json;

namespace azure.gremlin.cli.Models.ResultSet
{
    public class VertexResultElement : IResultElement
    {
        public string? Id { get; set; }
        public string? Label { get; set; }
        public Dictionary<string, List<PropertyValue>>? Properties { get; set; }
        public string GetLlmInput()
        {
            if (Label is null)
            {
                return $"{Label} is not valid";
            }
            else
            {
                if (Properties is not null)
                {
                    Dictionary<string, object> keyPropertyDictionary = new Dictionary<string, object>();
                    foreach (KeyValuePair<string, List<PropertyValue>> keyValuePair in Properties)
                    {
                        keyPropertyDictionary[keyValuePair.Key] = string.Empty;
                        List<PropertyValue> propertyValueList = keyValuePair.Value;
                        foreach (PropertyValue propertyValue in propertyValueList)
                        {
                            if (propertyValue.Value is not null)
                            {
                                keyPropertyDictionary[keyValuePair.Key] += propertyValue.Value;
                            }
                        }
                    }
                    return JsonConvert.SerializeObject(keyPropertyDictionary, Formatting.Indented);
                }
                else
                {
                    return $"Vertex {Label} does not contain data";
                }
            }
        }
        public class PropertyValue
        {
            public string? Id { get; set; }
            public string? Value { get; set; }
        }
    }
}