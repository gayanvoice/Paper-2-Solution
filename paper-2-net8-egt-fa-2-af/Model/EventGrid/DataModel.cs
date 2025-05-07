using Azure.Messaging.EventGrid;
using Newtonsoft.Json;

namespace FunctionApp.Model.EventGrid
{
    public class DataModel
    {
        public string? ModelId { get; set; }
        public List<object>? Patch { get; set; }
        public List<PatchModel> GetPatchModel()
        {
            List<PatchModel> patchModelList = new List<PatchModel>();
            if (Patch is not null)
            {
                foreach (object obj in Patch)
                {
                    if (obj is not null)
                    {
                        string patchString = obj.ToString() ?? string.Empty;
                        if (patchString is not null)
                        {
                            PatchModel? patchModel = new PatchModel();
                            try
                            {
                                patchModel = JsonConvert.DeserializeObject<PatchModel>(patchString);
                                if (patchModel is not null)
                                {
                                    patchModelList.Add(patchModel);
                                }
                            }
                            catch (Exception ex)
                            {
                            }
                        }
                    }
                }
            }
            return patchModelList;
        }
        public class PatchModel
        {
            [JsonProperty("value")]
            public object? Value { get; set; }

            [JsonProperty("path")]
            public string? Path { get; set; }

            [JsonProperty("op")]
            public string? Op { get; set; }
        }
    }
}