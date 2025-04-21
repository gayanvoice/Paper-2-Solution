namespace azure.gremlin.cli.Models.RequestScript
{
    public class AssetISVertexRequestScriptModel : RequestScriptModel, IRequestScript
    {
        public double Illuminance { get; set; }
        public AssetISVertexRequestScriptModel(string id, string name, double illuminance, string description)
        {
            Label = "asset_is";
            Id = id;
            Name = name;
            Illuminance = illuminance;
            Description = description;
            PartitionKey = "factory";
        }
        public string GetRequestScript()
        {
            return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('illuminance', {3}).property('description', '{4}').property('partitionKey', '{5}')", Label, Id, Name, Illuminance, Description, PartitionKey);
        }
    }
}