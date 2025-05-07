namespace azure.gremlin.cli.Models.RequestScript
{
    public class AddVertexRequestScript
    {
        public class PositionLabel
        {
            public class PositionVertexModel : RequestScript, IRequestScript
            {
                public string HasObject { get; set; }
                public PositionVertexModel(string id, string name, bool hasObject, string description)
                {
                    Label = VertexLabelEnum.Position;
                    PartitionKey = VertexPartitionKeyEnum.Factory;
                    Id = id;
                    Name = name;
                    HasObject = hasObject ? "True" : "False";
                    Description = description;
                }
                public string GetRequestScript()
                {
                    return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('has_object', '{3}').property('description', '{4}').property('partitionKey', '{5}')", Label.ToString(), Id, Name, HasObject, Description, PartitionKey.ToString());
                }
            }
        }
        public class ItemLabel
        {
            public class ItemVertexModel : RequestScript, IRequestScript
            {
                public string HasProcessed { get; set; }
                public ItemVertexModel(string id, string name, bool hasProcessed, string description)
                {
                    Label = VertexLabelEnum.Item;
                    PartitionKey = VertexPartitionKeyEnum.Factory;
                    Id = id;
                    Name = name;
                    HasProcessed = hasProcessed ? "True" : "False";
                    Description = description;
                }
                public string GetRequestScript()
                {
                    return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('has_processed', '{3}').property('description', '{4}').property('partitionKey', '{5}')", Label.ToString(), Id, Name, HasProcessed, Description, PartitionKey.ToString());
                }
            }
        }
        public class ProcessLabel
        {
            public class ProcessVertexModel : RequestScript, IRequestScript
            {
                public ProcessVertexModel(string id, string name, string description)
                {
                    Label = VertexLabelEnum.Process;
                    PartitionKey = VertexPartitionKeyEnum.Factory;
                    Id = id;
                    Name = name;
                    Description = description;
                }
                public string GetRequestScript()
                {
                    return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('description', '{3}').property('partitionKey', '{4}')", Label.ToString(), Id, Name, Description, PartitionKey.ToString());
                }
            }
        }
        public class AssetLabel
        {
            public class InfraredSensorVertexModel : RequestScript, IRequestScript
            {
                public string DetectObject { get; set; }
                public InfraredSensorVertexModel(string id, string name, bool detectObject, string description)
                {
                    Label = VertexLabelEnum.Asset;
                    PartitionKey = VertexPartitionKeyEnum.Factory;
                    Id = id;
                    Name = name;
                    DetectObject = detectObject ? "True" : "False"; ;
                    Description = description;
                }
                public string GetRequestScript()
                {
                    return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('status', '{3}').property('description', '{4}').property('partitionKey', '{5}')", Label.ToString(), Id, Name, DetectObject, Description, PartitionKey.ToString());
                }
            }

            public class IlluminanceSensorVertexModel : RequestScript, IRequestScript
            {
                public double Illuminance { get; set; }
                public IlluminanceSensorVertexModel(string id, string name, double illuminance, string description)
                {
                    Label = VertexLabelEnum.Asset;
                    PartitionKey = VertexPartitionKeyEnum.Factory;
                    Id = id;
                    Name = name;
                    Illuminance = illuminance;
                    Description = description;
                }
                public string GetRequestScript()
                {
                    return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('illuminance', {3}).property('description', '{4}').property('partitionKey', '{5}')", Label.ToString(), Id, Name, Illuminance, Description, PartitionKey.ToString());
                }
            }
            public class TemperatureSensorVertexModel : RequestScript, IRequestScript
            {
                public double Temperature { get; set; }
                public TemperatureSensorVertexModel(string id, string name, double temperature, string description)
                {
                    Label = VertexLabelEnum.Asset;
                    PartitionKey = VertexPartitionKeyEnum.Factory;
                    Id = id;
                    Name = name;
                    Temperature = temperature;
                    Description = description;
                }
                public string GetRequestScript()
                {
                    return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('tempeature', {3}).property('description', '{4}').property('partitionKey', '{5}')", Label.ToString(), Id, Name, Temperature, Description, PartitionKey.ToString());
                }
            }
            public class ControlBoardVertexModel : RequestScript, IRequestScript
            {
                public ControlBoardVertexModel(string id, string name, string description)
                {
                    Label = VertexLabelEnum.Asset;
                    PartitionKey = VertexPartitionKeyEnum.Factory;
                    Id = id;
                    Name = name;
                    Description = description;
                }
                public string GetRequestScript()
                {
                    return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('description', '{3}').property('partitionKey', '{4}')", Label.ToString(), Id, Name, Description, PartitionKey.ToString());
                }
            }
            public class URCobotVertexModel : RequestScript, IRequestScript
            {
                public string Status { get; set; }
                public string Position { get; set; }
                public URCobotVertexModel(string id, string name, string status, string position, string description)
                {
                    Label = VertexLabelEnum.Asset;
                    PartitionKey = VertexPartitionKeyEnum.Factory;
                    Id = id;
                    Name = name;
                    Status = status;
                    Position = position;
                    Description = description;
                }
                public string GetRequestScript()
                {
                    return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('status', '{3}').property('position', '{4}').property('description', '{5}').property('partitionKey', '{6}')", Label.ToString(), Id, Name, Status, Position, Description, PartitionKey.ToString());
                }
            }
            public class RobotiqGripperVertexModel : RequestScript, IRequestScript
            {
                public string Status { get; set; }
                public string Position { get; set; }
                public RobotiqGripperVertexModel(string id, string name, string status, string position, string description)
                {
                    Label = VertexLabelEnum.Asset;
                    PartitionKey = VertexPartitionKeyEnum.Factory;
                    Id = id;
                    Name = name;
                    Status = status;
                    Position = position;
                    Description = description;
                }
                public string GetRequestScript()
                {
                    return string.Format("g.addV('{0}').property('id', '{1}').property('name', '{2}').property('status', '{3}').property('position', '{4}').property('description', '{5}').property('partitionKey', '{6}')", Label.ToString(), Id, Name, Status, Position, Description, PartitionKey.ToString());
                }
            }
        }
    }
}