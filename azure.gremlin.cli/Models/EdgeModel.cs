namespace azure.gremlin.cli.Models
{
    public class EdgeModel : IResultElement
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
            return $"{InV} has {Label} to {OutV}";
        }
    }
}