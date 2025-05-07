using Newtonsoft.Json.Linq;
using Newtonsoft.Json;

namespace FunctionApp.Converters
{
    public class PayloadConverter<T> : JsonConverter
    {
        public override bool CanConvert(Type objectType) => objectType == typeof(T);

        public override object? ReadJson(JsonReader reader, Type objectType, object? existingValue, JsonSerializer serializer)
        {
            var token = JToken.Load(reader);
            if (token.Type == JTokenType.String)
            {
                var innerJson = token.ToString();
                return JsonConvert.DeserializeObject<T>(innerJson);
            }
            return token.ToObject<T>(serializer);
        }

        public override void WriteJson(JsonWriter writer, object? value, JsonSerializer serializer)
        {
            var json = JsonConvert.SerializeObject(value);
            writer.WriteValue(json);
        }
    }
}