namespace azure.gremlin.cli.Models
{
    public class VertexModel : IResultElement
    {
        public string? Id { get; set; }
        public string? Label { get; set; }
        public Dictionary<string, List<PropertyValue>>? Properties { get; set; }

        public string GetLlmInput()
        {
            return $"{Id} has {Label}";
        }

        public class PropertyValue
        {
            public string? Id { get; set; }
            public string? Value { get; set; }
        }
    }
}