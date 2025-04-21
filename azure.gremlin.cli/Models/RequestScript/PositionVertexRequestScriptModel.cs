namespace azure.gremlin.cli.Models.RequestScript
{
    public class PositionVertexRequestScriptModel : RequestScriptModel, IRequestScript
    {
        public string HasObject { get; set; }
        public PositionVertexRequestScriptModel(string id, string name, bool hasObject, string description)
        {
            Label = "position";
            Id = id;
            Name = name;
            HasObject = hasObject ? "True" : "False";
            Description = description;
            PartitionKey = "factory";
        }
        public string GetRequestScript()
        {
            return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('has_object', '{3}').property('description', '{4}').property('partitionKey', '{5}')", Label, Id, Name, HasObject, Description, PartitionKey);
        }
    }
}