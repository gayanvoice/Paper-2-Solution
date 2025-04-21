using System.Runtime.InteropServices.JavaScript;

namespace azure.gremlin.cli.Models.RequestScript
{
    public class ItemVertexRequestScriptModel : RequestScriptModel, IRequestScript
    {
        public string HasProcessed { get; set; }
        public ItemVertexRequestScriptModel(string id, string name, bool hasProcessed, string description)
        {
            Label = "item";
            Id = id;
            Name = name;
            HasProcessed= hasProcessed ? "True" : "False";
            Description = description;
            PartitionKey = "factory";
        }
        public string GetRequestScript()
        {
            return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('has_processed', '{3}').property('description', '{4}').property('partitionKey', '{5}')", Label, Id, Name, HasProcessed, Description, PartitionKey);
        }
    }
}