namespace azure.gremlin.cli.Models.RequestScript
{
    public class AssetTSVertexRequestScriptModel : RequestScriptModel, IRequestScript
    {
        public double Temperature { get; set; }
        public AssetTSVertexRequestScriptModel(string id, string name, double temperature, string description)
        {
            Label = "asset_ts";
            Id = id;
            Name = name;
            Temperature = temperature;
            Description = description;
            PartitionKey = "factory";
        }
        public string GetRequestScript()
        {
            return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('tempeature', {3}).property('description', '{4}').property('partitionKey', '{5}')", Label, Id, Name, Temperature, Description, PartitionKey);
        }
    }
}