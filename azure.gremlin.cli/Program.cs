using azure.gremlin.cli.Models;
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
using System.Text.Json;
using System.Xml;
using static azure.gremlin.cli.Models.ResultSetModel;

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

Dictionary<string, string> gremlinQueries = new Dictionary<string, string>{
    { "Cleanup",        "g.V().drop()" },

    { "AddVertex 1",    "g.addV('asset').property('id', 'robotiq_gripper').property('name', 'Robotiq Gripper').property('description', 'The Robotiq Gripper is mounted on the arm of UR Cobot to grasp and manipulate payload items').property('status', 'Not Activated').property('partitionKey', 'factory')" },
    { "AddVertex 2",    "g.addV('asset').property('id', 'ur_cobot').property('name', 'UR Cobot').property('description', 'The Universal Robots Cobot 10e (UR Cobot) is a collaborative robot used for performing pick-and-place tasks').property('status', 'Not Activated').property('joint_position', 'Home').property('partitionKey', 'factory')" },
    { "AddVertex 3",    "g.addV('asset').property('id', 'temperature_sensor').property('description', 'Monitors and logs the ambient temperature in the environment').property('degree_ceclsius', '16').property('partitionKey', 'factory')" },
    { "AddVertex 4",    "g.addV('asset').property('id', 'illuminance_sensor').property('description', 'Monitors and logs the ambient illumination in the environment').property('lux', '20').property('partitionKey', 'factory')" },
    { "AddVertex 5",    "g.addV('asset').property('id', 'infrared_sensor_1').property('description', 'An infrared sensor mounted unloading position 1').property('detect_object', 'False').property('partitionKey', 'factory')" },
    { "AddVertex 6",    "g.addV('asset').property('id', 'infrared_sensor_2').property('description', 'An infrared sensor mounted unloading position 2').property('detect_object', 'False').property('partitionKey', 'factory')" },
    { "AddVertex 7",    "g.addV('asset').property('id', 'infrared_sensor_3').property('description', 'An infrared sensor mounted loading position 1').property('detect_object', 'False').property('partitionKey', 'factory')" },
    { "AddVertex 8",    "g.addV('asset').property('id', 'infrared_sensor_4').property('description', 'An infrared sensor mounted loading position 2').property('detect_object', 'False').property('partitionKey', 'factory')" },
    { "AddVertex 9",    "g.addV('asset').property('id', 'control_board').property('description', 'The control board is mounted on the UR Cobot to manage input/output I/O) operations of sensors').property('partitionKey', 'factory')" },
    { "AddVertex 10",    "g.addV('asset').property('id', 'scanner_box').property('description', 'A secured environment housing the UR Cobot, Robotiq Gripper, and various sensors').property('partitionKey', 'factory')" },

    { "AddVertex 11",    "g.addV('process').property('id', 'unloading_position_1').property('description', 'Unloading Position 1 is designated for placing processed or unprocessed payload items').property('status', 'Empty and does not contain any payload items').property('partitionKey', 'factory')" },
    { "AddVertex 12",    "g.addV('process').property('id', 'unloading_position_2').property('description', 'Unloading Position 2 is designated for placing processed or unprocessed payload items').property('status', 'Empty and does not contain any payload items').property('partitionKey', 'factory')" },
    { "AddVertex 13",    "g.addV('process').property('id', 'loading_position_1').property('description', 'Loading Position 1 is designated for placing payload items to be processed').property('status', 'Empty and does not contain any payload items').property('partitionKey', 'factory')" },
    { "AddVertex 14",    "g.addV('process').property('id', 'loading_position_2').property('description', 'Loading Position 2 is designated for placing payload items to be processed').property('status', 'Empty and does not contain any payload items').property('partitionKey', 'factory')" },

    { "AddVertex 15",    "g.addV('item').property('id', 'item_1').property('description', 'A payload item intended for processing').property('status', 'The payload item remains unprocessed').property('partitionKey', 'factory')" },
    { "AddVertex 16",    "g.addV('item').property('id', 'item_2').property('description', 'A payload item intended for processing').property('status', 'The payload item has been processed').property('partitionKey', 'factory')" },

    { "AddEdge 1",      "g.V('scanner_box').addE('has').to(g.V('robotiq_gripper'))" },
    { "AddEdge 2",      "g.V('scanner_box').addE('has').to(g.V('ur_cobot'))" },
    { "AddEdge 3",      "g.V('ur_cobot').addE('has').to(g.V('control_board'))" },
    { "AddEdge 4",      "g.V('control_board').addE('connected').to(g.V('temperature_sensor'))" },
    { "AddEdge 5",      "g.V('control_board').addE('connected').to(g.V('illuminance_sensor'))" },
    { "AddEdge 6",      "g.V('control_board').addE('connected').to(g.V('infrared_sensor_1'))" },
    { "AddEdge 7",      "g.V('control_board').addE('connected').to(g.V('infrared_sensor_2'))" },
    { "AddEdge 8",      "g.V('control_board').addE('connected').to(g.V('infrared_sensor_3'))" },
    { "AddEdge 9",      "g.V('control_board').addE('connected').to(g.V('infrared_sensor_4'))" },

    { "AddEdge 10",      "g.V('infrared_sensor_1').addE('describes').to(g.V('unloading_position_1'))" },
    { "AddEdge 11",      "g.V('infrared_sensor_2').addE('describes').to(g.V('unloading_position_2'))" },
    { "AddEdge 12",      "g.V('infrared_sensor_3').addE('describes').to(g.V('loading_position_1'))" },
    { "AddEdge 13",      "g.V('infrared_sensor_4').addE('describes').to(g.V('loading_position_2'))" },

    { "AddEdge 14",      "g.V('unloading_position_1').addE('placed').to(g.V('item_1'))" },
    { "AddEdge 15",      "g.V('unloading_position_2').addE('placed').to(g.V('item_2'))" }
};
GremlinGraph gremlinGraph = new GremlinGraph(gremlinClient);

foreach (KeyValuePair<string, string> keyvaluePair in gremlinQueries)
{
    ResultSetModel resultSetModel = await gremlinGraph.SubmitAsync(keyvaluePair);
    if (resultSetModel.ResultType == azure.gremlin.cli.Enums.ResultTypeEnum.VERTEX)
    {
        Console.WriteLine(resultSetModel.GetLlmInput());
    }
    if (resultSetModel.ResultType == azure.gremlin.cli.Enums.ResultTypeEnum.EDGE)
    {
        Console.WriteLine(resultSetModel.GetLlmInput());
    }
}
Console.WriteLine("completed");

public class GremlinGraph
{
    private GremlinClient _gremlinClient;
    public GremlinGraph(GremlinClient gremlinClient)
    {
        _gremlinClient = gremlinClient;
    }
    public async Task<ResultSetModel> SubmitAsync(KeyValuePair<string, string> keyvaluePair)
    {
        try
        {
            ResultSet<dynamic> resultSet = await _gremlinClient.SubmitAsync<dynamic>(keyvaluePair.Value);
            ResultSetModel resultSetModel = new ResultSetModel();
            resultSetModel.SetRequest(keyvaluePair);
            resultSetModel.SetResponse(resultSet);
            return resultSetModel;
        }
        catch (ResponseException e)
        {
            Console.WriteLine($"StatusCode: {e.StatusCode}");
            throw;
        }
    }
   
}