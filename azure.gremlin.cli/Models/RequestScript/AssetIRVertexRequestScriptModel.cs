namespace azure.gremlin.cli.Models.RequestScript
{
    public class AssetIRVertexRequestScriptModel : RequestScriptModel, IRequestScript
    {
        public string DetectObject { get; set; }
        public AssetIRVertexRequestScriptModel(string id, string name, bool detectObject, string description)
        {
            Label = "asset_ir";
            Id = id;
            Name = name;
            DetectObject = detectObject ? "True" : "False"; ;
            Description = description;
            PartitionKey = "factory";
        }
        public string GetRequestScript()
        {
            return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('status', '{3}').property('description', '{4}').property('partitionKey', '{5}')", Label, Id, Name, DetectObject, Description, PartitionKey);
        }
    }
}