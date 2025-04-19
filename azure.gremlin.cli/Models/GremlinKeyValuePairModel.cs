namespace azure.gremlin.cli.Models
{
    public class GremlinKeyValuePairModel
    {
        public string? Key { get; set; }
        public string? Value { get; set; }
        public static GremlinKeyValuePairModel Create(KeyValuePair<string, string> keyvaluePair)
        {
            GremlinKeyValuePairModel gremlinKeyValuePairModel = new GremlinKeyValuePairModel();
            gremlinKeyValuePairModel.Key = keyvaluePair.Key;
            gremlinKeyValuePairModel.Value = keyvaluePair.Value;
            return gremlinKeyValuePairModel;
        }
    }
}