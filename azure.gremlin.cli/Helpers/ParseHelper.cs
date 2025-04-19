using System.Text.Json;

namespace azure.gremlin.cli.Helpers
{
    public class ParseHelper
    {
        public static object? GetValueOrDefault(IReadOnlyDictionary<string, object> dictionary, string key)
        {
            if (dictionary.TryGetValue(key, out var value))
            {
                if (value is JsonElement element)
                {
                    return ExtractJsonValue(element);
                }

                return value;
            }
            return null;
        }
        public static object? ExtractJsonValue(JsonElement element)
        {
            switch (element.ValueKind)
            {
                case JsonValueKind.Number:
                    if (element.TryGetInt32(out int i))
                        return i;
                    if (element.TryGetDouble(out double d))
                        return d;
                    break;

                case JsonValueKind.String:
                    return element.GetString();

                case JsonValueKind.True:
                case JsonValueKind.False:
                    return element.GetBoolean();

                case JsonValueKind.Null:
                case JsonValueKind.Undefined:
                    return null;
            }
            return element.ToString();
        }
    }
}