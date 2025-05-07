namespace azure.gremlin.cli.Models.RequestScript
{
    public class AddEdgeRequestScript : IRequestScript
    {
        public string? EdgeId { get; set; }
        public string? SourceId { get; set; }
        public string? TargetId { get; set; }
        public AddEdgeRequestScript(string sourceId, string edgeId, string targetId)
        {
            SourceId = sourceId;
            EdgeId = edgeId;
            TargetId = targetId;
        }
        public string GetRequestScript()
        {
            return string.Format("g.V('{0}').addE('{1}').to(g.V('{2}'))", SourceId, EdgeId, TargetId);
        }
    }
}