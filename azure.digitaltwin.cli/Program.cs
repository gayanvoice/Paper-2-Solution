using Azure.DigitalTwins.Core;
using Azure.Identity;
using Azure.ResourceManager.DigitalTwins;
using Azure.ResourceManager.Resources;
using Azure.ResourceManager;

const string tenentId = "c263ac0d-270a-43fd-95d1-e279d1002ff9";
const string resourceGroupName = "paper-2-rg";
const string resourceName = "paper-2-adt-1";

Console.WriteLine("starting azure.digitaltwin.cli");

Console.WriteLine("authenticating azure");

Console.WriteLine("check web browser for login");

InteractiveBrowserCredential interactiveBrowserCredential = new InteractiveBrowserCredential(new InteractiveBrowserCredentialOptions() { TenantId = tenentId });
ArmClient armClient = new ArmClient(interactiveBrowserCredential);
SubscriptionResource subscriptionResource = await armClient.GetDefaultSubscriptionAsync();
ResourceGroupCollection resourceGroupCollection = subscriptionResource.GetResourceGroups();
ResourceGroupResource resourceGroupResource = await resourceGroupCollection.GetAsync(resourceGroupName);
DigitalTwinsDescriptionResource digitalTwinsDescriptionResource = await resourceGroupResource.GetDigitalTwinsDescriptionAsync(resourceName: resourceName);
Uri digitalTwinsUri = new UriBuilder(Uri.UriSchemeHttps, digitalTwinsDescriptionResource.Data.HostName).Uri;
DigitalTwinsClient digitalTwinsClient = new DigitalTwinsClient(new Uri(digitalTwinsUri.ToString()), interactiveBrowserCredential);

Console.WriteLine("successfully authenticated");

Console.WriteLine("creating digital twins");

DigitalTwin digitalTwin = new DigitalTwin(digitalTwinsClient);

Console.WriteLine("creating factory dt");
await digitalTwin.createTwinAsync("factory", "dtmi:com:physical_twins:factory;1");

Console.WriteLine("creating illuminance_sensor_1 dt");
await digitalTwin.createTwinAsync("illuminance_sensor_1", "dtmi:com:physical_twins:factory:sensor:illuminance_sensor:illuminance_sensor_1;1");

Console.WriteLine("creating infrared_sensor dt");
await digitalTwin.createTwinAsync("infrared_sensor", "dtmi:com:physical_twins:factory:sensor:infrared_sensor;1");

Console.WriteLine("creating infrared_sensor_1 dt");
await digitalTwin.createTwinAsync("infrared_sensor_1", "dtmi:com:physical_twins:factory:sensor:infrared_sensor:infrared_sensor_1;1");

Console.WriteLine("creating infrared_sensor_2 dt");
await digitalTwin.createTwinAsync("infrared_sensor_2", "dtmi:com:physical_twins:factory:sensor:infrared_sensor:infrared_sensor_2;1");

Console.WriteLine("creating infrared_sensor_3 dt");
await digitalTwin.createTwinAsync("infrared_sensor_3", "dtmi:com:physical_twins:factory:sensor:infrared_sensor:infrared_sensor_3;1");

Console.WriteLine("creating infrared_sensor_4 dt");
await digitalTwin.createTwinAsync("infrared_sensor_4", "dtmi:com:physical_twins:factory:sensor:infrared_sensor:infrared_sensor_4;1");

Console.WriteLine("creating robotiq_gripper dt");
await digitalTwin.createTwinAsync("robotiq_gripper", "dtmi:com:physical_twins:factory:robotiq_gripper;1");

Console.WriteLine("creating sensor dt");
await digitalTwin.createTwinAsync("sensor", "dtmi:com:physical_twins:factory:sensor;1");

Console.WriteLine("creating temperature_sensor dt");
await digitalTwin.createTwinAsync("temperature_sensor", "dtmi:com:physical_twins:factory:sensor:temperature_sensor;1");

Console.WriteLine("creating temperature_sensor_1 dt");
await digitalTwin.createTwinAsync("temperature_sensor_1", "dtmi:com:physical_twins:factory:sensor:temperature_sensor:temperature_sensor_1;1");

Console.WriteLine("creating ur_cobot dt");
await digitalTwin.createTwinAsync("ur_cobot", "dtmi:com:physical_twins:factory:ur_cobot;1");

Console.WriteLine("creating relationships");

Console.WriteLine("creating factory-has-sensor relationship");
await digitalTwin.createRelationshipAsync("factory", "sensor", "has_sensor");

Console.WriteLine("creating factory-has_ur_cobot relationship");
await digitalTwin.createRelationshipAsync("factory", "ur_cobot", "has_ur_cobot");

Console.WriteLine("creating factory-robotiq_gripper relationship");
await digitalTwin.createRelationshipAsync("factory", "robotiq_gripper", "has_robotiq_gripper");

Console.WriteLine("creating sensor-temperature_sensor relationship");
await digitalTwin.createRelationshipAsync("sensor", "temperature_sensor", "has_temperature_sensor");

Console.WriteLine("creating sensor-illuminance_sensor relationship");
await digitalTwin.createRelationshipAsync("sensor", "illuminance_sensor", "has_illuminance_sensor");

Console.WriteLine("creating sensor-infrared_sensor relationship");
await digitalTwin.createRelationshipAsync("sensor", "infrared_sensor", "has_infrared_sensor");

Console.WriteLine("creating temperature_sensor-temperature_sensor_1 relationship");
await digitalTwin.createRelationshipAsync("temperature_sensor", "temperature_sensor_1", "has_temperature_sensor_1");

Console.WriteLine("creating illuminance_sensor-illuminance_sensor_1 relationship");
await digitalTwin.createRelationshipAsync("illuminance_sensor", "illuminance_sensor_1", "has_illuminance_sensor_1");

Console.WriteLine("creating infrared_sensor-illuminance_sensor_1 relationship");
await digitalTwin.createRelationshipAsync("infrared_sensor", "infrared_sensor_1", "has_infrared_sensor_1");

Console.WriteLine("creating infrared_sensor-illuminance_sensor_2 relationship");
await digitalTwin.createRelationshipAsync("infrared_sensor", "infrared_sensor_2", "has_infrared_sensor_2");

Console.WriteLine("creating infrared_sensor-illuminance_sensor_3 relationship");
await digitalTwin.createRelationshipAsync("infrared_sensor", "infrared_sensor_3", "has_infrared_sensor_3");

Console.WriteLine("creating infrared_sensor-illuminance_sensor_4 relationship");
await digitalTwin.createRelationshipAsync("infrared_sensor", "infrared_sensor_4", "has_infrared_sensor_4");

Console.WriteLine("completed");

public class DigitalTwin
{
    private DigitalTwinsClient _digitalTwinsClient;
    public DigitalTwin(DigitalTwinsClient DigitalTwinsClient)
    {
        _digitalTwinsClient = DigitalTwinsClient;
    }
    public async Task createTwinAsync(string id, string modelId)
    {
        BasicDigitalTwin basicDigitalTwin = new BasicDigitalTwin
        {
            Id = id,
            Metadata = { ModelId = modelId },
            Contents = { },
        };
        await _digitalTwinsClient.CreateOrReplaceDigitalTwinAsync<BasicDigitalTwin>(basicDigitalTwin.Id, basicDigitalTwin);
    }
    public async Task createRelationshipAsync(string sourceId, string targetId, string name)
    {
        BasicRelationship basicRelationship = new BasicRelationship();
        basicRelationship.TargetId = targetId;
        basicRelationship.Name = name;
        string relationshipId = $"{sourceId}-{name}-{targetId}";
        await _digitalTwinsClient.CreateOrReplaceRelationshipAsync<BasicRelationship>(digitalTwinId: sourceId, relationshipId: relationshipId, relationship: basicRelationship);
    }
}