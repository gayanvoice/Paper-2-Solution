namespace azure.gremlin.cli.Models.ResultSet
{
    public class IntegerResultElement : IResultElement
    {
        public IntegerResultElement(int number)
        {
            Number = number;
        }
        public int Number { get; set; }
        public string GetLlmInput()
        {
            return Number.ToString();
        }
    }
}