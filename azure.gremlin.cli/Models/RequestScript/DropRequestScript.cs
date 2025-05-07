namespace azure.gremlin.cli.Models.RequestScript
{
    public class DropRequestScript : IRequestScript
    {
        public string GetRequestScript()
        {
            return string.Format("g.V().drop()");
        }
    }
}