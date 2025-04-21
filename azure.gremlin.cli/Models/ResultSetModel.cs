using azure.gremlin.cli.Enums;
using azure.gremlin.cli.Models.RequestScript;
using Gremlin.Net.Driver;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace azure.gremlin.cli.Models
{
    public class ResultSetModel
    {
        public ResultTypeEnum? ResultType { get; set; }
        public ResponseTypeEnum? ResponseType { get; set; }
        public IRequestScript? RequestScript { get; set; }
        public ICollection<IResultElement>? ResultElementCollection { get; set; }
        public CosmosDbResponseMetadataModel? CosmosDbResponseMetadata { get; set; }
        public void SetRequest(IRequestScript requestScript)
        {
            RequestScript = requestScript;
        }
        public void SetResponse(ResultSet<dynamic> resultSet)
        {
            CosmosDbResponseMetadata = CosmosDbResponseMetadataModel.Create(resultSet);
            ResponseType = SetResponseType();
            ResultElementCollection = SetResultElementCollection(resultSet);
            ResultType = CreateResultType(resultSet);
        }
        public List<IResultElement> SetResultElementCollection(ResultSet<dynamic> resultSet)
        {
            List<IResultElement> resultElementCollection = new List<IResultElement>();
            if (resultSet.Count > 0)
            {
                foreach (var result in resultSet)
                {
                    string output = JsonConvert.SerializeObject(result);
                    IResultElement? resultElement = CreateResultElement(output);
                    if (resultElement is not null)
                    {
                        resultElementCollection.Add(resultElement);
                    }
                }
            }
            return resultElementCollection;
        }
        public string? GetLlmInput()
        {
            if (ResultElementCollection is null)
            {
                return "The knowledge graph does not contain anything related to request";
            }
            else
            {
                if (ResultElementCollection.Count is 0)
                {
                    return "The knowledge graph contains 0 results related to request";
                }
                else
                {
                    string output = string.Empty;
                    foreach (IResultElement resultElement in ResultElementCollection)
                    {
                        output += resultElement.GetLlmInput() + ". ";
                    }
                    return output;
                }
            }
        }
        private IResultElement? CreateResultElement(string json)
        {
            var jObject = JObject.Parse(json);
            var type = jObject["type"]?.ToString();
            return type switch
            {
                "vertex" => jObject.ToObject<VertexModel>(),
                "edge" => jObject.ToObject<EdgeModel>(),
                _ => throw new NotImplementedException()
            };
        }
        public ResultTypeEnum CreateResultType(ResultSet<dynamic> resultSet)
        {
            ResultTypeEnum resultTypeEnum;
            List<IResultElement> resultElementList = SetResultElementCollection(resultSet);
            if (resultElementList.Count == 0)
            {
                resultTypeEnum = ResultTypeEnum.NO_RESULT;
            }
            else {
                List<ResultTypeEnum>  resultTypeEnumList = resultElementList.Select(resultElement =>
                {
                    if (resultElement is VertexModel) return ResultTypeEnum.VERTEX;
                    if (resultElement is EdgeModel) return ResultTypeEnum.EDGE;
                    return ResultTypeEnum.OTHER;
                }).Distinct().ToList();

                if (resultTypeEnumList.Count == 1) resultTypeEnum = resultTypeEnumList.First();
                else resultTypeEnum = ResultTypeEnum.MIXED;
            }
            return resultTypeEnum;
        }
        private ResponseTypeEnum SetResponseType()
        {
            if (CosmosDbResponseMetadata == null)
            {
                return ResponseTypeEnum.FAILED;
            }
            else
            {
                if (CosmosDbResponseMetadata.StatusCode == 200)
                {
                    return ResponseTypeEnum.SUCCESS;
                }
                else if (CosmosDbResponseMetadata.StatusCode == 429)
                {
                    return ResponseTypeEnum.THROTTLED;
                }
                else if (CosmosDbResponseMetadata.StatusCode == 408)
                {
                    return ResponseTypeEnum.TIMEOUT;
                }
                else
                {
                    return ResponseTypeEnum.FAILED;
                }
            }
        }
    }
}