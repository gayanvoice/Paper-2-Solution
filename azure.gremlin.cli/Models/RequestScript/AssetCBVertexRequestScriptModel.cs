namespace azure.gremlin.cli.Models.RequestScript
{
    public class AssetCBVertexRequestScriptModel : RequestScriptModel, IRequestScript
    {
        public AssetCBVertexRequestScriptModel(string id, string name, string description)
        {
            Label = "asset_cb";
            Id = id;
            Name = name;
            Description = description;
            PartitionKey = "factory";
        }
        public string GetRequestScript()
        {
            return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('description', '{3}').property('partitionKey', '{4}')", Label, Id, Name, Description, PartitionKey);
        }
    }
}