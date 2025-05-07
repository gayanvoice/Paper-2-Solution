namespace azure.gremlin.cli.Models.RequestScript
{
    public class SortRequestScript : IRequestScript
    {
        public string RequestScript { get; set; }
        public SortRequestScript(string requestScript)
        {
            RequestScript = requestScript;
        }
        public string GetRequestScript()
        {
            return RequestScript;
        }
    }
}