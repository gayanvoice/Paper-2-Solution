namespace azure.gremlin.cli.Models
{
    public class VertexModel : IResultElement
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
                    string output = string.Empty;
                    foreach (KeyValuePair<string, List<PropertyValue>> keyValuePair in Properties)
                    {
                        List<PropertyValue> values = keyValuePair.Value;
                        foreach (PropertyValue value in values)
                        {

                            output += $"{keyValuePair.Key} is {value.Value}, ";
                        }
                    }
                    return output;
                }
                else
                {
                    return $"{Label} does not contain data";
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