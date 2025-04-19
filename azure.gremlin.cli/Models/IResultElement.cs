using System.Reflection.Emit;

namespace azure.gremlin.cli.Models
{
    public interface IResultElement
    {
        public string GetLlmInput();
    }
}