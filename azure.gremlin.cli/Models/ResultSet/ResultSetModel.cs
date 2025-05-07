using azure.gremlin.cli.Enums;
using azure.gremlin.cli.Models.RequestScript;
using Gremlin.Net.Driver;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace azure.gremlin.cli.Models.ResultSet
{
    public class ResultSetModel
    {
        public ResultSetModel(IRequestScript requestScript, ResultSet<dynamic> resultSet)
        {
            RequestScript = requestScript;
            ResponseMetadata = ResponseMetadataModel.Create(resultSet);
            ResponseType = SetResponseType();
            ResultElementCollection = SetResultElementCollection(resultSet);
            ResultType = SetResultType(resultSet);
        }
        public string? ResultType { get; set; }
        public string? ResponseType { get; set; }
        public IRequestScript? RequestScript { get; set; }
        public ICollection<IResultElement>? ResultElementCollection { get; set; }
        public ResponseMetadataModel? ResponseMetadata { get; set; }

        public List<IResultElement> SetResultElementCollection(ResultSet<dynamic> resultSet)
        {
            List<IResultElement> resultElementCollection = new List<IResultElement>();
            if (resultSet.Count > 0)
            {
                foreach (dynamic result in resultSet)
                {
                    if (result is string)
                    {
                        resultElementCollection.Add(new StringResultElement(result));
                    }
                    else if (result is int)
                    {
                        resultElementCollection.Add(new IntegerResultElement(result));
                    }
                    else if (result is long)
                    {
                        resultElementCollection.Add(new LongResultElement(result));
                    }
                    else if (result is Dictionary<string, object>)
                    {
                        IResultElement? resultElement;
                        JObject jObject = JObject.Parse(JsonConvert.SerializeObject(result));
                        string? type = jObject["type"]?.ToString();
                        if (type is null)
                        {
                            throw new NotImplementedException();
                        }
                        else
                        {
                            if (type is "vertex")
                            {
                                resultElement = jObject.ToObject<VertexResultElement>();
                            }
                            else if (type is "edge")
                            {
                                resultElement = jObject.ToObject<EdgeResultElement>();
                            }
                            else
                            {
                                throw new NotImplementedException();
                            }
                        }
                        if (resultElement is not null)
                        {
                            resultElementCollection.Add(resultElement);
                        }
                    }
                    else if (result is JArray)
                    {
                        throw new NotImplementedException();
                    }
                    else
                    {
                        throw new NotImplementedException();
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
                        output += resultElement.GetLlmInput();
                    }
                    return output;
                }
            }
        }
        public string SetResultType(ResultSet<dynamic> resultSet)
        {
            ResultTypeEnum resultTypeEnum;
            List<IResultElement> resultElementList = SetResultElementCollection(resultSet);
            if (resultElementList.Count == 0)
            {
                resultTypeEnum = ResultTypeEnum.NO_RESULT;
            }
            else 
            {
                dynamic result = resultSet.First();
                if (result is string)
                {
                    resultTypeEnum = ResultTypeEnum.STRING_RESULT;
                }
                else if (result is int)
                {
                    resultTypeEnum = ResultTypeEnum.INTEGER_RESULT;
                }
                else if (result is long)
                {
                    resultTypeEnum = ResultTypeEnum.LONG_RESULT;
                }
                else if (result is Dictionary<string, object>)
                {
                    JObject jObject = JObject.Parse(JsonConvert.SerializeObject(result));
                    string? type = jObject["type"]?.ToString();
                    if (type is null)
                    {
                        throw new NotImplementedException();
                    }
                    else
                    {
                        if (type is "vertex")
                        {
                            resultTypeEnum = ResultTypeEnum.VERTEX_OBJECT;
                        }
                        else if (type is "edge")
                        {
                            resultTypeEnum = ResultTypeEnum.EDGE_OBJECT;
                        }
                        else
                        {
                            throw new NotImplementedException();
                        }
                    }
                }
                else if (result is JArray)
                {
                    resultTypeEnum = ResultTypeEnum.ARRAY_RESULT;
                }
                else
                {
                    throw new NotImplementedException();
                }
            }
            return resultTypeEnum.ToString();
        }
        private string SetResponseType()
        {
            ResponseTypeEnum responseTypeEnum;
            if (ResponseMetadata == null)
            {
                responseTypeEnum = ResponseTypeEnum.NO_RESPONSE;
            }
            else
            {
                if (ResponseMetadata.StatusCode == 200)
                {
                    responseTypeEnum = ResponseTypeEnum.SUCCESS;
                }
                else if (ResponseMetadata.StatusCode == 429)
                {
                    responseTypeEnum = ResponseTypeEnum.THROTTLED;
                }
                else if (ResponseMetadata.StatusCode == 408)
                {
                    responseTypeEnum = ResponseTypeEnum.TIMEOUT;
                }
                else
                {
                    responseTypeEnum = ResponseTypeEnum.FAILED;
                }
            }
            return responseTypeEnum.ToString();
        }
    }
}