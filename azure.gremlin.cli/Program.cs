using azure.gremlin.cli.Models;
using azure.gremlin.cli.Models.RequestScript;
using azure.gremlin.cli.Readers;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.CosmosDB;
using Azure.ResourceManager.CosmosDB.Models;
using Azure.ResourceManager.Resources;
using Gremlin.Net.Driver;
using Gremlin.Net.Driver.Exceptions;
using Gremlin.Net.Structure.IO.GraphSON;
using Newtonsoft.Json;

const string tenentId = "c263ac0d-270a-43fd-95d1-e279d1002ff9";
const string resourceGroupName = "paper-2-rg";
const string accountName = "paper-2-acdb-ag-1";
const string databaseName = "graphdb";
const string graphName = "factory-g";

Console.WriteLine("starting azure.gremlin.cli");

Console.WriteLine("authenticating azure");

Console.WriteLine("check web browser for login");

InteractiveBrowserCredential interactiveBrowserCredential = new InteractiveBrowserCredential(new InteractiveBrowserCredentialOptions() { TenantId = tenentId });
ArmClient armClient = new ArmClient(interactiveBrowserCredential);
SubscriptionResource subscriptionResource = await armClient.GetDefaultSubscriptionAsync();
ResourceGroupCollection resourceGroupCollection = subscriptionResource.GetResourceGroups();
ResourceGroupResource resourceGroupResource = await resourceGroupCollection.GetAsync(resourceGroupName);
CosmosDBAccountResource cosmosDBAccountResource = await resourceGroupResource.GetCosmosDBAccountAsync(accountName: accountName);

Console.WriteLine("successfully authenticated");

CosmosDBAccountKeyList cosmosDBAccountKeyList = await cosmosDBAccountResource.GetKeysAsync();
GremlinDatabaseResource gremlinDatabaseResource = await cosmosDBAccountResource.GetGremlinDatabaseAsync(databaseName);
GremlinGraphResource gremlinGraphResource = await gremlinDatabaseResource.GetGremlinGraphAsync(graphName);

string primaryMasterKey = cosmosDBAccountKeyList.PrimaryMasterKey;
string sdkUri = cosmosDBAccountResource.Data.DocumentEndpoint;
string gremlinUri = $"{accountName}.gremlin.cosmos.azure.com:443/";

Console.WriteLine($"SDK URI: {sdkUri}");
Console.WriteLine($"Gremlin URI: {gremlinUri}");
Console.WriteLine($"Primary Master Key: {primaryMasterKey}");

GremlinServer gremlinServer = new GremlinServer(
    hostname: gremlinUri,
    port: 443,
    username: $"/dbs/{gremlinDatabaseResource.Data.Name}/colls/{gremlinGraphResource.Data.Name}",
    password: $"{primaryMasterKey}",
    enableSsl: true
);

GremlinClient gremlinClient = new GremlinClient(gremlinServer: gremlinServer, messageSerializer: new GraphSON2MessageSerializer(new CustomGraphSON2Reader()));

Console.WriteLine($"gremlin client has {gremlinClient.NrConnections} connections");

List<IRequestScript> requestScriptList = new List<IRequestScript>();
requestScriptList.Add(new DropRequestScriptModel());
requestScriptList.Add(new ProcessVertexRequestScriptModel(id: "factory", name: "Factory", description: "has assets, processes, and items"));
requestScriptList.Add(new ProcessVertexRequestScriptModel(id: "items", name: "Items", description: "has items"));
requestScriptList.Add(new ProcessVertexRequestScriptModel(id: "loadingbay", name: "Loading Bay", description: "a secure environment housing assets"));
requestScriptList.Add(new ProcessVertexRequestScriptModel(id: "positions", name: "Positions", description: "has loading and unloading positions"));
requestScriptList.Add(new ProcessVertexRequestScriptModel(id: "loading_positions", name: "Loading Positions", description: "has loading positions"));
requestScriptList.Add(new ProcessVertexRequestScriptModel(id: "unloading_positions", name: "Unloading Positions", description: "has unloading positions"));

requestScriptList.Add(new PositionVertexRequestScriptModel(id: "loading_position_1", name: "Loading Position 1", hasObject: false, description: "designated for placing payload items to be processed"));
requestScriptList.Add(new PositionVertexRequestScriptModel(id: "loading_position_2", name: "Loading Position 2", hasObject: false, description: "designated for placing payload items to be processed"));
requestScriptList.Add(new PositionVertexRequestScriptModel(id: "unloading_position_1", name: "Unloading Position 1", hasObject: false, description: "designated for placing processed or unprocessed payload items"));
requestScriptList.Add(new PositionVertexRequestScriptModel(id: "unloading_position_2", name: "Unloading Position 2", hasObject: false, description: "designated for placing processed or unprocessed payload items"));

requestScriptList.Add(new ItemVertexRequestScriptModel(id: "item_1", name: "Item 1", hasProcessed: false, description: "ready for processing"));
requestScriptList.Add(new ItemVertexRequestScriptModel(id: "item_2", name: "Item 2", hasProcessed: true, description: "already processed"));

requestScriptList.Add(new AssetRGVertexRequestScriptModel(id: "robotiq_gripper", name: "Robotiq Gripper", status: "disabled", position: "closed", description: "a robotic gripper mounted on the arm of UR Cobot to grasp and manipulate payload items"));

requestScriptList.Add(new AssetUCVertexRequestScriptModel(id: "ur_cobot", name: "UR Cobot", status: "disabled", position: "home", description: "a collaborative robot used for performing pick-and-place tasks"));

requestScriptList.Add(new AssetCBVertexRequestScriptModel(id: "control_board", name: "Control Board", description: "mounted on the UR Cobot to manage input/output I/O) operations of sensors"));

requestScriptList.Add(new AssetTSVertexRequestScriptModel(id: "temperature_sensor_1", name: "Temperature Sensor 1", temperature: 16.666, description: "records ambient temperature in the environment"));

requestScriptList.Add(new AssetISVertexRequestScriptModel(id: "illuminance_sensor_1", name: "Illuminance Sensor 1", illuminance: 20, description: "records ambient illumination in the environment"));

requestScriptList.Add(new AssetIRVertexRequestScriptModel(id: "infrared_sensor_1", name: "Infrared Sensor 1", detectObject: false, description: "mounted on unloading position 1"));
requestScriptList.Add(new AssetIRVertexRequestScriptModel(id: "infrared_sensor_2", name: "Infrared Sensor 2", detectObject: false, description: "mounted on unloading position 2"));
requestScriptList.Add(new AssetIRVertexRequestScriptModel(id: "infrared_sensor_3", name: "Infrared Sensor 3", detectObject: false, description: "mounted on loading position 1"));
requestScriptList.Add(new AssetIRVertexRequestScriptModel(id: "infrared_sensor_4", name: "Infrared Sensor 4", detectObject: true, description: "mounted on loading position 2"));

requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "positions", edgeId: "part_of", targetId: "factory"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "items", edgeId: "part_of", targetId: "factory"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "loadingbay", edgeId: "part_of", targetId: "factory"));

requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "loading_positions", edgeId: "are_in", targetId: "positions"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "unloading_positions", edgeId: "are_in", targetId: "positions"));

requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "loading_position_1", edgeId: "is_in", targetId: "loading_positions"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "loading_position_2", edgeId: "is_in", targetId: "loading_positions"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "unloading_position_1", edgeId: "is_in", targetId: "unloading_positions"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "unloading_position_2", edgeId: "is_in", targetId: "unloading_positions"));

requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "item_1", edgeId: "associated_with", targetId: "items"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "item_2", edgeId: "associated_with", targetId: "items"));

requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "robotiq_gripper", edgeId: "integrated_with", targetId: "loadingbay"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "ur_cobot", edgeId: "integrated_with", targetId: "loadingbay"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "control_board", edgeId: "integrated_with", targetId: "ur_cobot"));

requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "temperature_sensor_1", edgeId: "connected_to", targetId: "control_board"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "illuminance_sensor_1", edgeId: "connected_to", targetId: "control_board"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "infrared_sensor_1", edgeId: "connected_to", targetId: "control_board"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "infrared_sensor_2", edgeId: "connected_to", targetId: "control_board"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "infrared_sensor_3", edgeId: "connected_to", targetId: "control_board"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "infrared_sensor_4", edgeId: "connected_to", targetId: "control_board"));

requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "item_1", edgeId: "placed_at", targetId: "loading_position_1"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "item_1", edgeId: "handled_by", targetId: "robotiq_gripper"));
requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "item_1", edgeId: "handled_by", targetId: "ur_cobot"));

requestScriptList.Add(new EdgeRequestScriptModel(sourceId: "item_2", edgeId: "placed_at", targetId: "unloading_position_1"));



//Dictionary<string, string> gremlinQueries = new Dictionary<string, string>{
//    { "Cleanup",        "g.V().drop()" },

//    { "AddVertex 1", "g.addV('process').property('id', 'factory').property('name', 'Factory').property('description', 'has assets, processes, and items').property('partitionKey', 'factory')" },
//    { "AddVertex 2", "g.addV('process').property('id', 'items').property('name', 'Items').property('description', 'has items').property('partitionKey', 'factory')" },
//    { "AddVertex 3", "g.addV('process').property('id', 'loadingbay').property('name', 'Loading Bay').property('description', 'a secure environment housing assets').property('partitionKey', 'factory')" },
//    { "AddVertex 4", "g.addV('process').property('id', 'positions').property('name', 'Positions').property('description', 'has loading and unloading positions').property('partitionKey', 'factory')" },
//    { "AddVertex 5", "g.addV('process').property('id', 'loading_positions').property('name', 'Loading Positions').property('description', 'has loading positions').property('partitionKey', 'factory')" },
//    { "AddVertex 6", "g.addV('process').property('id', 'unloading_positions').property('name', 'Unloading Positions').property('description', 'has unloading positions').property('partitionKey', 'factory')" },

//    { "AddVertex 7", "g.addV('position').property('id', 'loading_position_1').property('name', 'Loading Position 1').property('has_object', 'False').property('description', 'designated for placing payload items to be processed').property('partitionKey', 'factory')" },
//    { "AddVertex 8", "g.addV('position').property('id', 'loading_position_2').property('name', 'Loading Position 2').property('has_object', 'False').property('description', 'designated for placing payload items to be processed').property('partitionKey', 'factory')" },
//    { "AddVertex 9", "g.addV('position').property('id', 'unloading_position_1').property('name', 'Unloading Position 1').property('has_object', 'False').property('description', 'designated for placing processed or unprocessed payload items').property('partitionKey', 'factory')" },
//    { "AddVertex 10", "g.addV('position').property('id', 'unloading_position_2').property('name', 'Unloading Position 2').property('has_object', 'False').property('description', 'designated for placing processed or unprocessed payload items').property('partitionKey', 'factory')" },

//    { "AddVertex 11", "g.addV('item').property('id', 'item_1').property('name', 'Item 1').property('has_processed', 'False').property('description', 'ready for processing').property('partitionKey', 'factory')" },
//    { "AddVertex 12", "g.addV('item').property('id', 'item_2').property('name', 'Item 1').property('has_processed', 'True').property('description', 'already processed').property('partitionKey', 'factory')" },
    
//    { "AddVertex 13", "g.addV('asset_rg').property('id', 'robotiq_gripper').property('name', 'Robotiq Gripper').property('status', 'disabled').property('position', 'closed').property('description', 'a robotic gripper mounted on the arm of UR Cobot to grasp and manipulate payload items').property('partitionKey', 'factory')" },

//    { "AddVertex 14", "g.addV('asset_uc').property('id', 'ur_cobot').property('name', 'UR Cobot').property('status', 'disabled').property('position', 'home').property('description', 'a collaborative robot used for performing pick-and-place tasks').property('joint_position', 'Home').property('partitionKey', 'factory')" },

//    { "AddVertex 15", "g.addV('asset_cb').property('id', 'control_board').property('name', 'Control Board').property('description', 'mounted on the UR Cobot to manage input/output I/O) operations of sensors').property('partitionKey', 'factory')" },

//    { "AddVertex 16", "g.addV('asset_ts').property('id', 'temperature_sensor').property('name', 'Temperature Sensor 1').property('tempeature_in_celsius', 16.666).property('description', 'recorded ambient temperature in the environment').property('partitionKey', 'factory')" },

//    { "AddVertex 17", "g.addV('asset_is').property('id', 'illuminance_sensor').property('name', 'Illuminance Sensor').property('illuminance_in_lux', 20).property('description', 'recorded ambient illumination in the environment').property('partitionKey', 'factory')" },

//    { "AddVertex 18", "g.addV('asset_ir').property('id', 'infrared_sensor_1').property('name', 'Infrared Sensor 1').property('status', 'False').property('description', 'mounted unloading position 1').property('partitionKey', 'factory')" },
//    { "AddVertex 19", "g.addV('asset_ir').property('id', 'infrared_sensor_2').property('name', 'Infrared Sensor 2').property('status', 'False').property('description', 'mounted unloading position 2').property('partitionKey', 'factory')" },
//    { "AddVertex 20", "g.addV('asset_ir').property('id', 'infrared_sensor_3').property('name', 'Infrared Sensor 3').property('status', 'False').property('description', 'mounted loading position 1').property('partitionKey', 'factory')" },
//    { "AddVertex 21", "g.addV('asset_ir').property('id', 'infrared_sensor_4').property('name', 'Infrared Sensor 4').property('status', 'True').property('description', 'mounted loading position 2').property('partitionKey', 'factory')" },

//    { "AddEdge 1", "g.V('positions').addE('are_in').to(g.V('factory'))" },
//    { "AddEdge 2", "g.V('items').addE('are_in').to(g.V('factory'))" },
//    { "AddEdge 3", "g.V('loadingbay').addE('is_in').to(g.V('factory'))" },

//    { "AddEdge 4", "g.V('loading_positions').addE('are_in').to(g.V('positions'))" },
//    { "AddEdge 5", "g.V('unloading_positions').addE('are_in').to(g.V('positions'))" },

//    { "AddEdge 6", "g.V('loading_position_1').addE('is_in').to(g.V('loading_positions'))" },
//    { "AddEdge 7", "g.V('loading_position_2').addE('is_in').to(g.V('loading_positions'))" },

//    { "AddEdge 8", "g.V('unloading_position_1').addE('is_in').to(g.V('unloading_positions'))" },
//    { "AddEdge 9", "g.V('unloading_position_2').addE('is_in').to(g.V('unloading_positions'))" },

//    { "AddEdge 10", "g.V('item_1').addE('associated_with').to(g.V('items'))" },
//    { "AddEdge 11", "g.V('item_2').addE('associated_with').to(g.V('items'))" },

//    { "AddEdge 12", "g.V('robotiq_gripper').addE('integrated_with').to(g.V('loadingbay'))" },
//    { "AddEdge 13", "g.V('ur_cobot').addE('integrated_with').to(g.V('loadingbay'))" },

//    { "AddEdge 14", "g.V('control_board').addE('is_in').to(g.V('ur_cobot'))" },

//    { "AddEdge 15", "g.V('temperature_sensor').addE('connected_to').to(g.V('control_board'))" },
//    { "AddEdge 16", "g.V('illuminance_sensor').addE('connected_to').to(g.V('control_board'))" },
//    { "AddEdge 17", "g.V('infrared_sensor_1').addE('connected_to').to(g.V('control_board'))" },
//    { "AddEdge 18", "g.V('infrared_sensor_2').addE('connected_to').to(g.V('control_board'))" },
//    { "AddEdge 19", "g.V('infrared_sensor_3').addE('connected_to').to(g.V('control_board'))" },
//    { "AddEdge 20", "g.V('infrared_sensor_4').addE('connected_to').to(g.V('control_board'))" },

//    { "AddEdge 21", "g.V('item_1').addE('placed_at').to(g.V('loading_position_1'))" },
//    { "AddEdge 22", "g.V('item_1').addE('handled_by').to(g.V('robotiq_gripper'))" },
//    { "AddEdge 23", "g.V('item_1').addE('handled_by').to(g.V('ur_cobot'))" },

//    { "AddEdge 24", "g.V('item_2').addE('placed_at').to(g.V('unloading_position_1'))" },

//    //{ "Sort", "g.V().hasLabel('asset').order().by('id', decr)" },
//    //{ "Filter", "g.V().hasLabel('asset').has('id', 'temperature_sensor')" },
//    //{ "Traverse", "g.V('infrared_sensor_1').out('describes').hasLabel('process')" },
//    //{ "Traverse 2X", "g.V('infrared_sensor_1').out('describes').hasLabel('process').out('placed').hasLabel('item')" },


//};
GremlinGraph gremlinGraph = new GremlinGraph(gremlinClient);

foreach (IRequestScript requestScript in requestScriptList)
{
    ResultSetModel resultSetModel = await gremlinGraph.SubmitAsync(requestScript);
    //if (resultSetModel.ResultType == azure.gremlin.cli.Enums.ResultTypeEnum.NO_RESULT)
    //{
    //    Console.WriteLine("NO_RESULT");
    //}
    //if (resultSetModel.ResultType == azure.gremlin.cli.Enums.ResultTypeEnum.VERTEX)
    //{
    //    Console.WriteLine("VERTEX: " + resultSetModel.GetLlmInput());
    //}
    //if (resultSetModel.ResultType == azure.gremlin.cli.Enums.ResultTypeEnum.EDGE)
    //{
    //    Console.WriteLine("EDGE: " + resultSetModel.GetLlmInput());
    //}
}
Console.WriteLine("completed");

public class GremlinGraph
{
    private GremlinClient _gremlinClient;
    public GremlinGraph(GremlinClient gremlinClient)
    {
        _gremlinClient = gremlinClient;
    }
    public async Task<ResultSetModel> SubmitAsync(IRequestScript requestScript)
    {
        try
        {
            ResultSet<dynamic> resultSet = await _gremlinClient.SubmitAsync<dynamic>(requestScript.GetRequestScript());
            ResultSetModel resultSetModel = new ResultSetModel();
            resultSetModel.SetRequest(requestScript);
            resultSetModel.SetResponse(resultSet);
            Console.WriteLine(JsonConvert.SerializeObject(resultSetModel, Formatting.Indented));
            return resultSetModel;
        }
        catch (ResponseException e)
        {
            Console.WriteLine($"StatusCode: {e.StatusCode}");
            throw;
        }
    }
   
}