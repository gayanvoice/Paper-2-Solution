namespace azure.gremlin.cli.Models.RequestScript
{
    public class DropRequestScriptModel : IRequestScript
    {
        public string GetRequestScript()
        {
            return string.Format("g.V().drop()");
        }
    }
}