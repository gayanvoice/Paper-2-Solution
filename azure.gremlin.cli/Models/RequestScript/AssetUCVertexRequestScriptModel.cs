namespace azure.gremlin.cli.Models.RequestScript
{
    public class AssetUCVertexRequestScriptModel : RequestScriptModel, IRequestScript
    {
        public string Status{ get; set; }
        public string Position{ get; set; }
        public AssetUCVertexRequestScriptModel(string id, string name, string status, string position, string description)
        {
            Label = "asset_uc";
            Id = id;
            Name = name;
            Status= status;
            Position = position;
            Description = description;
            PartitionKey = "factory";
        }
        public string GetRequestScript()
        {
            return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('status', '{3}').property('position', '{4}').property('description', '{5}').property('partitionKey', '{6}')", Label, Id, Name, Status, Position, Description, PartitionKey);
        }
    }
}