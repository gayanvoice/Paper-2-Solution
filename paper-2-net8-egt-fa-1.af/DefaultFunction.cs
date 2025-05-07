using Azure.Messaging.EventGrid;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json;
using static System.Runtime.InteropServices.JavaScript.JSType;
using System.Diagnostics;
using Azure.DigitalTwins.Core;
using Azure.Identity;
using Azure;
using FunctionApp.Model.URCobot.Control;
using FunctionApp.Model.URCobot.Shared;
using FunctionApp.Model.RobotiqGripper.Control;
using FunctionApp.Model.Sensor;

namespace FunctionApp
{
    public class DefaultFunction
    {
        private readonly ILogger<DefaultFunction> _logger;
        private readonly string? EV_ADT_SERVICE_URL;
        private readonly string? EV_SQLDBS_CONNECTION_STRING;
        private readonly DigitalTwinsClient _digitalTwinsClient;
        private readonly string? rootId;
        private readonly Stopwatch _stopwatch;
        private readonly DateTime _startDateTime;

        public DefaultFunction(ILogger<DefaultFunction> logger)
        {
            _logger = logger;
            _stopwatch = new Stopwatch();
            _stopwatch.Start();
            _startDateTime = DateTime.Now;

            EV_ADT_SERVICE_URL = Environment.GetEnvironmentVariable("EV_ADT_SERVICE_URL");
            EV_SQLDBS_CONNECTION_STRING = Environment.GetEnvironmentVariable("EV_SQLDBS_CONNECTION_STRING");
            if (Activity.Current is not null) rootId = Activity.Current.RootId;
            if (EV_ADT_SERVICE_URL is null)
            {
                _logger.LogError($"[{rootId}] application setting 'EV_ADT_SERVICE_URL' not set", rootId);
                return;
            }
            if (EV_SQLDBS_CONNECTION_STRING is null)
            {
                _logger.LogError($"[{rootId}] application setting 'EV_SQLDBS_CONNECTION_STRING' not set", rootId);
                return;
            }
            DefaultAzureCredential defaultAzureCredential = new DefaultAzureCredential();
            _digitalTwinsClient = new DigitalTwinsClient(new Uri(EV_ADT_SERVICE_URL), defaultAzureCredential);
        }

        [Function(nameof(DefaultFunction))]
        public async Task RunAsync([EventGridTrigger] EventGridEvent eventGridEvent)
        {
            _logger.LogInformation("[{rootId}] started {type}", rootId, nameof(DefaultFunction));
            try
            {
                _logger.LogInformation("[{rootId}] adt service client connection created.", rootId);

                if (eventGridEvent is not null && eventGridEvent.Data is not null)
                {
                    _logger.LogInformation("[{rootId}] valid event grid event", rootId);
                    string data = eventGridEvent.Data.ToString();
                    JObject? dataJObject = JsonConvert.DeserializeObject<JObject>(data);
                    if (dataJObject is not null)
                    {
                        JObject? systemPropertiesJObject = dataJObject["systemProperties"] as JObject;
                        JObject? bodyJObject = dataJObject["body"] as JObject;

                        if (systemPropertiesJObject is not null && bodyJObject is not null)
                        {
                            JValue? iothubConnectionDeviceIdJObject = (JValue?)systemPropertiesJObject["iothub-connection-device-id"];
                            if (iothubConnectionDeviceIdJObject is not null)
                            {
                                string iotHubConnectionDeviceId = iothubConnectionDeviceIdJObject.ToString();
                                _logger.LogInformation("[{rootId}] iothub-connection-device-id: {iotHubConnectionDeviceId}", rootId, iotHubConnectionDeviceId);

                                if (iotHubConnectionDeviceId.Equals("ur_cobot"))
                                {
                                    _logger.LogInformation("[{rootId}] updating ur_cobot", rootId);
                                    await UpdateURCobotTwin(bodyJObject);
                                    await UpdateTemperatureSensor1Twin(bodyJObject);
                                    await UpdateIlluminanceSensor1Twin(bodyJObject);
                                    await UpdateInfraredSensor1Twin(bodyJObject);
                                    await UpdateInfraredSensor2Twin(bodyJObject);
                                    await UpdateInfraredSensor3Twin(bodyJObject);
                                    await UpdateInfraredSensor4Twin(bodyJObject);
                                    DateTime endDateTime = DateTime.Now;
                                    _stopwatch.Stop();
                                    _logger.LogInformation("[{rootId}] updated ur_cobot digital twin successfully", rootId);

                                }
                                else if (iotHubConnectionDeviceId.Equals("robotiq_gripper"))
                                {
                                    _logger.LogInformation("[{rootId}] updating robotiq gripper", rootId);
                                    await UpdateRobotiqGripperTwin(bodyJObject);
                                    DateTime endDateTime = DateTime.Now;
                                    _stopwatch.Stop();
                                    _logger.LogInformation("[{rootId}] updated robotiq_gripper digital twin", rootId);
                                }
                                else
                                {
                                    _logger.LogWarning("[{rootId}] unknown iothub-connection-device-id: {iothub-connection-device-id}", rootId, iotHubConnectionDeviceId);
                                }
                            }
                        }
                    }
                }
                else
                {
                    _logger.LogError("[{rootId}] event grid event is null", rootId);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex.ToString());
            }
            finally
            {
                _logger.LogInformation("[{rootId}] ended {type}", rootId, nameof(DefaultFunction));
            }
        }
        private async Task UpdateURCobotTwin(JObject bodyJObject)
        {
            JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
            azureJsonPatchDocument.AppendAdd("/var_target_q", Position6Model.GetPosition6Model(positionToken: bodyJObject["target_q"]));
            azureJsonPatchDocument.AppendAdd("/var_target_qd", Position6Model.GetPosition6Model(positionToken: bodyJObject["target_qd"]));
            azureJsonPatchDocument.AppendAdd("/var_target_qdd", Position6Model.GetPosition6Model(positionToken: bodyJObject["target_qdd"]));
            azureJsonPatchDocument.AppendAdd("/var_target_current", Position6Model.GetPosition6Model(positionToken: bodyJObject["target_current"]));
            azureJsonPatchDocument.AppendAdd("/var_target_moment", Position6Model.GetPosition6Model(positionToken: bodyJObject["target_moment"]));
            azureJsonPatchDocument.AppendAdd("/var_actual_current", Position6Model.GetPosition6Model(positionToken: bodyJObject["actual_current"]));
            azureJsonPatchDocument.AppendAdd("/var_actual_q", Position6Model.GetPosition6Model(positionToken: bodyJObject["actual_q"]));
            azureJsonPatchDocument.AppendAdd("/var_actual_qd", Position6Model.GetPosition6Model(positionToken: bodyJObject["actual_qd"]));
            azureJsonPatchDocument.AppendAdd("/var_joint_control_output", Position6Model.GetPosition6Model(positionToken: bodyJObject["joint_control_output"]));
            azureJsonPatchDocument.AppendAdd("/var_actual_tcp_force", Position6Model.GetPosition6Model(positionToken: bodyJObject["actual_tcp_force"]));
            azureJsonPatchDocument.AppendAdd("/var_joint_temperatures", Position6Model.GetPosition6Model(positionToken: bodyJObject["joint_temperatures"]));
            azureJsonPatchDocument.AppendAdd("/var_joint_mode", Position6Model.GetPosition6Model(positionToken: bodyJObject["joint_mode"]));
            azureJsonPatchDocument.AppendAdd("/var_actual_tool_accelerometer", Position3Model.GetPosition3Model(positionToken: bodyJObject["actual_tool_accelerometer"]));
            azureJsonPatchDocument.AppendAdd("/var_speed_scaling", Convert.ToDouble(bodyJObject["speed_scaling"]));
            azureJsonPatchDocument.AppendAdd("/var_actual_momentum", Convert.ToDouble(bodyJObject["actual_momentum"]));
            azureJsonPatchDocument.AppendAdd("/var_actual_main_voltage", Convert.ToDouble(bodyJObject["actual_main_voltage"]));
            azureJsonPatchDocument.AppendAdd("/var_actual_robot_voltage", Convert.ToDouble(bodyJObject["actual_robot_voltage"]));
            azureJsonPatchDocument.AppendAdd("/var_actual_robot_current", Convert.ToDouble(bodyJObject["actual_robot_current"]));
            azureJsonPatchDocument.AppendAdd("/var_actual_joint_voltage", Position6Model.GetPosition6Model(positionToken: bodyJObject["actual_joint_voltage"]));
            azureJsonPatchDocument.AppendAdd("/var_runtime_state", Convert.ToInt32(bodyJObject["runtime_state"]));
            azureJsonPatchDocument.AppendAdd("/var_robot_mode", Convert.ToInt32(bodyJObject["robot_mode"]));
            azureJsonPatchDocument.AppendAdd("/var_safety_mode", Convert.ToInt32(bodyJObject["safety_mode"]));
            azureJsonPatchDocument.AppendAdd("/var_analog_io_types", Convert.ToInt32(bodyJObject["analog_io_types"]));
            azureJsonPatchDocument.AppendAdd("/var_io_current", Convert.ToDouble(bodyJObject["io_current"]));
            azureJsonPatchDocument.AppendAdd("/var_tool_mode", Convert.ToInt32(bodyJObject["tool_mode"]));
            azureJsonPatchDocument.AppendAdd("/var_tool_output_voltage", Convert.ToInt32(bodyJObject["tool_output_voltage"]));
            azureJsonPatchDocument.AppendAdd("/var_tool_output_current", Convert.ToDouble(bodyJObject["tool_output_current"]));
            azureJsonPatchDocument.AppendAdd("/var_standard_analog_out_0", Convert.ToDouble(bodyJObject["standard_analog_out_0"]));
            azureJsonPatchDocument.AppendAdd("/var_standard_analog_out_1", Convert.ToDouble(bodyJObject["standard_analog_out_1"]));
            azureJsonPatchDocument.AppendAdd("/var_standard_digital_out_0", Convert.ToBoolean(bodyJObject["standard_digital_out_0"]));
            azureJsonPatchDocument.AppendAdd("/var_standard_digital_out_1", Convert.ToBoolean(bodyJObject["standard_digital_out_1"]));
            azureJsonPatchDocument.AppendAdd("/var_standard_digital_out_2", Convert.ToBoolean(bodyJObject["standard_digital_out_2"]));
            azureJsonPatchDocument.AppendAdd("/var_standard_digital_out_3", Convert.ToBoolean(bodyJObject["standard_digital_out_3"]));
            azureJsonPatchDocument.AppendAdd("/var_standard_digital_out_4", Convert.ToBoolean(bodyJObject["standard_digital_out_4"]));
            azureJsonPatchDocument.AppendAdd("/var_standard_digital_out_5", Convert.ToBoolean(bodyJObject["standard_digital_out_5"]));
            azureJsonPatchDocument.AppendAdd("/var_standard_digital_out_6", Convert.ToBoolean(bodyJObject["standard_digital_out_6"]));
            azureJsonPatchDocument.AppendAdd("/var_standard_digital_out_7", Convert.ToBoolean(bodyJObject["standard_digital_out_7"]));
            //azureJsonPatchDocument.AppendAdd("/control_move_j", MoveJControlModel.GetMoveJControlModel(jToken: bodyJObject["target_q"]));
            //azureJsonPatchDocument.AppendAdd("/control_open_popup", OpenPopupControlModel.GetOpenPopupControlModel());
            //azureJsonPatchDocument.AppendAdd("/control_close_popup", ClosePopupControlModel.GetClosePopupControlModel());
            //azureJsonPatchDocument.AppendAdd("/control_close_safety_popup", CloseSafetyPopupControlModel.GetCloseSafetyPopupControlModel());
            //azureJsonPatchDocument.AppendAdd("/control_power_off", PowerOffControlModel.GetPowerOffControlModel());
            //azureJsonPatchDocument.AppendAdd("/control_power_on", PowerOnControlModel.GetPowerOnControlModel());
            //azureJsonPatchDocument.AppendAdd("/control_start_free_drive", StartFreeDriveControlModel.GetStartFreeDriveControlModel());
            //azureJsonPatchDocument.AppendAdd("/control_stop_free_drive", StopFreeDriveControlModel.GetStopFreeDriveControlModel());
            //azureJsonPatchDocument.AppendAdd("/control_unlock_protective_stop", UnlockProtectiveStopControlModel.GetUnlockProtectiveStopControlModel());
            await _digitalTwinsClient.UpdateDigitalTwinAsync("ur_cobot", azureJsonPatchDocument);
        }
        private async Task UpdateTemperatureSensor1Twin(JObject bodyJObject)
        {
            TemperatureSensorModel temperatureSensorModel = new TemperatureSensorModel(Convert.ToDouble(bodyJObject["standard_analog_out_0"]));
            await _digitalTwinsClient.UpdateDigitalTwinAsync("temperature_sensor_1", temperatureSensorModel.GetJsonPatchDocument(_logger));
        }
        private async Task UpdateIlluminanceSensor1Twin(JObject bodyJObject)
        {
            IlluminanceSensorModel illuminanceSensorModel = new IlluminanceSensorModel(Convert.ToDouble(bodyJObject["standard_analog_out_1"]));
            await _digitalTwinsClient.UpdateDigitalTwinAsync("illuminance_sensor_1", illuminanceSensorModel.GetJsonPatchDocument(_logger));
        }
        private async Task UpdateInfraredSensor1Twin(JObject bodyJObject)
        {
            InfraredSensorModel infraredSensorModel = new InfraredSensorModel(Convert.ToBoolean(bodyJObject["standard_digital_out_0"]));
            await _digitalTwinsClient.UpdateDigitalTwinAsync("infrared_sensor_1", infraredSensorModel.GetJsonPatchDocument(_logger));
        }
        private async Task UpdateInfraredSensor2Twin(JObject bodyJObject)
        {
            InfraredSensorModel infraredSensorModel = new InfraredSensorModel(Convert.ToBoolean(bodyJObject["standard_digital_out_1"]));
            await _digitalTwinsClient.UpdateDigitalTwinAsync("infrared_sensor_2", infraredSensorModel.GetJsonPatchDocument(_logger));
        }
        private async Task UpdateInfraredSensor3Twin(JObject bodyJObject)
        {
            InfraredSensorModel infraredSensorModel = new InfraredSensorModel(Convert.ToBoolean(bodyJObject["standard_digital_out_2"]));
            await _digitalTwinsClient.UpdateDigitalTwinAsync("infrared_sensor_3", infraredSensorModel.GetJsonPatchDocument(_logger));
        }
        private async Task UpdateInfraredSensor4Twin(JObject bodyJObject)
        {
            InfraredSensorModel infraredSensorModel = new InfraredSensorModel(Convert.ToBoolean(bodyJObject["standard_digital_out_3"]));
            await _digitalTwinsClient.UpdateDigitalTwinAsync("infrared_sensor_4", infraredSensorModel.GetJsonPatchDocument(_logger));
        }
        private async Task UpdateRobotiqGripperTwin(JObject bodyJObject)
        {
            JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
            azureJsonPatchDocument.AppendAdd("/var_act", Convert.ToInt32(bodyJObject["act"]));
            azureJsonPatchDocument.AppendAdd("/var_flt", Convert.ToInt32(bodyJObject["flt"]));
            azureJsonPatchDocument.AppendAdd("/var_for", Convert.ToInt32(bodyJObject["for"]));
            azureJsonPatchDocument.AppendAdd("/var_gto", Convert.ToInt32(bodyJObject["gto"]));
            azureJsonPatchDocument.AppendAdd("/var_obj", Convert.ToInt32(bodyJObject["obj"]));
            azureJsonPatchDocument.AppendAdd("/var_pos", Convert.ToInt32(bodyJObject["pos"]));
            azureJsonPatchDocument.AppendAdd("/var_pre", Convert.ToInt32(bodyJObject["pre"]));
            azureJsonPatchDocument.AppendAdd("/var_spe", Convert.ToInt32(bodyJObject["spe"]));
            azureJsonPatchDocument.AppendAdd("/var_sta", Convert.ToInt32(bodyJObject["sta"]));
            //azureJsonPatchDocument.AppendAdd("/control_activate_gripper", ActivateGripperControlModel.GetActivateGripperControlModel());
            //azureJsonPatchDocument.AppendAdd("/control_open_gripper", OpenGripperControlModel.GetOpenGripperControlModel());
            //azureJsonPatchDocument.AppendAdd("/control_close_gripper", CloseGripperControlModel.GetCloseGripperControlModel());
            await _digitalTwinsClient.UpdateDigitalTwinAsync("robotiq_gripper", azureJsonPatchDocument);
        }
    }
}