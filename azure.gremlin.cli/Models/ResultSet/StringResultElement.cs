namespace azure.gremlin.cli.Models.ResultSet
{
    public class StringResultElement : IResultElement
    {
        public StringResultElement(string text)
        {
            Text = text;
        }
        public string? Text { get; set; }
        public string GetLlmInput()
        {
            if (Text is null)
            {
                return "NULL Text";
            }
            else
            {
                return Text;
            }
        }
    }
}