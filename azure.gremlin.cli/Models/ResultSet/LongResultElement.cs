namespace azure.gremlin.cli.Models.ResultSet
{
    public class LongResultElement : IResultElement
    {
        public LongResultElement(long number)
        {
            Number = number;
        }
        public long Number { get; set; }
        public string GetLlmInput()
        {
            return Number.ToString();
        }
    }
}