namespace azure.gremlin.cli.Models.RequestScript
{
    public class RequestScript
    {
        public VertexLabelEnum Label { get; set; }
        public string? Id { get; set; }
        public string? Name { get; set; }
        public string? Description { get; set; }
        public VertexPartitionKeyEnum PartitionKey { get; set; }
    }
}