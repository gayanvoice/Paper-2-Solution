// Default URL for triggering event grid function in the local environment.
// http://localhost:7071/runtime/webhooks/EventGrid?functionName={functionname}

using Azure.Messaging.EventGrid;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Azure.DigitalTwins.Core;
using Azure.Identity;
using Newtonsoft.Json;
using Microsoft.Azure.Devices;
using FunctionApp.Model.EventGrid;
using Azure;
using static FunctionApp.Model.EventGrid.DataModel;
using FunctionApp.Model.InternetOfThings;
using System.Diagnostics;
using Microsoft.Extensions.DependencyInjection;
using FunctionApp.Model.DigitalTwins.RobotiqGripper.Control;
using FunctionApp.Model.URCobot.Control;


namespace FunctionApp
{
    public class DefaultFunction
    {
        private readonly ILogger<DefaultFunction> _logger;
        private static readonly string? ADT_SERVICE_URL = Environment.GetEnvironmentVariable("ADT_SERVICE_URL");
        private static readonly string? AIOT_HUB_SERVICE_URL = Environment.GetEnvironmentVariable("AIOT_HUB_SERVICE_URL");

        private static readonly string UR_COBOT_DEVICE_ID = "ur_cobot";
        private static readonly string UR_COBOT_DIGITAL_TWIN_ID = "ur_cobot";

        private static readonly string ROBOTIQ_GRIPPER_DEVICE_ID = "robotiq_gripper";
        private static readonly string ROBOTIQ_GRIPPER_DIGITAL_TWIN_ID = "robotiq_gripper";

        public DefaultFunction(ILogger<DefaultFunction> logger)
        {
            _logger = logger;
        }

        [Function(nameof(DefaultFunction))]
        public async Task RunAsync([EventGridTrigger] EventGridEvent eventGridEvent)
        {
            Stopwatch stopwatch = new Stopwatch();
            stopwatch.Start();
            try
            {
                if (ADT_SERVICE_URL is null)
                {
                    _logger.LogError("ADT_SERVICE_URL is null");
                    return;
                }
                if (AIOT_HUB_SERVICE_URL is null)
                {
                    _logger.LogError("AIOT_HUB_SERVICE_URL is null");
                    return;
                }
                DefaultAzureCredential defaultAzureCredential = new DefaultAzureCredential();
                DigitalTwinsClient digitalTwinsClient = new DigitalTwinsClient(endpoint: new Uri(ADT_SERVICE_URL), credential: defaultAzureCredential);
                if (eventGridEvent is not null && eventGridEvent.Data is not null)
                {
                    RootObjectModel? rootObjectModel = JsonConvert.DeserializeObject<RootObjectModel>(eventGridEvent.Data.ToString());
                    if (rootObjectModel is not null && rootObjectModel.Data is not null && rootObjectModel.Data.ModelId is not null)
                    {
                        List<PatchModel> patchModelList = rootObjectModel.Data.GetPatchModel();
                        if (rootObjectModel.Data.ModelId.Equals("dtmi:com:physical_twins:factory:ur_cobot;1"))
                        {
                            if (patchModelList is not null)
                            {
                                if (patchModelList.Count >= 1)
                                {
                                    PatchModel? patchModel = patchModelList
                                        .Where(x => x is not null && x.Path is not null && x.Path.Contains("RequestPayload"))
                                        .FirstOrDefault();
                                    if (patchModel is not null)
                                    {
                                        switch (patchModel.Path)
                                        {
                                            case "/control_move_j/RequestPayload/IsCommandRequested":
                                                if (patchModel.Value is true)
                                                {
                                                    _logger.LogInformation(rootObjectModel.Data.ModelId, patchModel.Path);
                                                    PatchModel? basePatchValueModel = patchModelList
                                                       .Where(x => x is not null && x.Path is not null && x.Path.Contains("/control_move_j/Base"))
                                                       .FirstOrDefault();
                                                    PatchModel? shoulderPatchValueModel = patchModelList
                                                       .Where(x => x is not null && x.Path is not null && x.Path.Contains("/control_move_j/Shoulder"))
                                                       .FirstOrDefault();
                                                    PatchModel? elbowPatchValueModel = patchModelList
                                                       .Where(x => x is not null && x.Path is not null && x.Path.Contains("/control_move_j/Elbow"))
                                                       .FirstOrDefault();
                                                    PatchModel? wrist1PatchValueModel = patchModelList
                                                       .Where(x => x is not null && x.Path is not null && x.Path.Contains("/control_move_j/Wrist1"))
                                                       .FirstOrDefault();
                                                    PatchModel? wrist2PatchValueModel = patchModelList
                                                       .Where(x => x is not null && x.Path is not null && x.Path.Contains("/control_move_j/Wrist2"))
                                                       .FirstOrDefault();
                                                    PatchModel? wrist3PatchValueModel = patchModelList
                                                       .Where(x => x is not null && x.Path is not null && x.Path.Contains("/control_move_j/Wrist3"))
                                                       .FirstOrDefault();
                                                    JointPositionModel jointPositionModel = new JointPositionModel();

                                                    if ((basePatchValueModel is not null && basePatchValueModel.Value is not null) &&
                                                        (shoulderPatchValueModel is not null && shoulderPatchValueModel.Value is not null) &&
                                                        (elbowPatchValueModel is not null && elbowPatchValueModel.Value is not null) &&
                                                        (wrist1PatchValueModel is not null && wrist1PatchValueModel.Value is not null) &&
                                                        (wrist2PatchValueModel is not null && wrist2PatchValueModel.Value is not null) &&
                                                        (wrist3PatchValueModel is not null && wrist3PatchValueModel.Value is not null))
                                                    {
                                                        jointPositionModel.Base = Convert.ToDouble(basePatchValueModel.Value.ToString());
                                                        jointPositionModel.Shoulder = Convert.ToDouble(shoulderPatchValueModel.Value.ToString());
                                                        jointPositionModel.Elbow = Convert.ToDouble(elbowPatchValueModel.Value.ToString());
                                                        jointPositionModel.Wrist1 = Convert.ToDouble(wrist1PatchValueModel.Value.ToString());
                                                        jointPositionModel.Wrist2 = Convert.ToDouble(wrist2PatchValueModel.Value.ToString());
                                                        jointPositionModel.Wrist3 = Convert.ToDouble(wrist3PatchValueModel.Value.ToString());
                                                    }
                                                    else
                                                    {
                                                        jointPositionModel.Base = -91.71;
                                                        jointPositionModel.Shoulder = -98.96;
                                                        jointPositionModel.Elbow = -126.22;
                                                        jointPositionModel.Wrist1 = -46.29;
                                                        jointPositionModel.Wrist2 = 91.39;
                                                        jointPositionModel.Wrist3 = -1.78;
                                                    }
                                                    JointPositionModelArrayItem jointPositionModelArrayItem = new JointPositionModelArrayItem();
                                                    jointPositionModelArrayItem.JointPositionModel = jointPositionModel;
                                                    List<JointPositionModelArrayItem> jointPositionModelArrayItemList = new List<JointPositionModelArrayItem>
                                                    {
                                                        jointPositionModelArrayItem
                                                    };
                                                    object requestPayload = new
                                                    {
                                                        _acceleration = 0.25,
                                                        _velocity = 0.25,
                                                        _time_s = 0.25,
                                                        _blend_radius = 0.0,
                                                        _joint_position_model_array = jointPositionModelArrayItemList
                                                    };
                                                    ResponseModel responseModel = await GetResponseModelAsync(UR_COBOT_DEVICE_ID, "MoveJCommand", requestPayload);
                                                    JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
                                                    azureJsonPatchDocument.AppendAdd(patchModel.Path, false);
                                                    azureJsonPatchDocument.AppendAdd("/control_move_j", MoveJControlModel.GetControlModel(jointPositionModel, responseModel));
                                                    await digitalTwinsClient.UpdateDigitalTwinAsync(UR_COBOT_DIGITAL_TWIN_ID, azureJsonPatchDocument);
                                                    _logger.LogInformation($"{patchModel.Path} executed succesfully");
                                                }
                                                break;
                                            case "/control_open_popup/RequestPayload/IsCommandRequested":
                                                if (patchModel.Value is true)
                                                {
                                                    _logger.LogInformation(rootObjectModel.Data.ModelId, patchModel.Path);
                                                    PatchModel? popupTextPatchModel = patchModelList
                                                        .Where(x => x is not null && x.Path is not null && x.Path.Contains("/control_open_popup/PopupText"))
                                                        .FirstOrDefault();
                                                    string popUpText = "Empty String";
                                                    if (popupTextPatchModel is not null && popupTextPatchModel.Value is not null)
                                                    {
                                                        popUpText = popupTextPatchModel.Value.ToString() ?? string.Empty;
                                                    }
                                                    object requestPayload = new
                                                    {
                                                        popup_text = popUpText,
                                                    };
                                                    ResponseModel responseModel = await GetResponseModelAsync(UR_COBOT_DEVICE_ID, "OpenPopupCommand", requestPayload);
                                                    JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
                                                    azureJsonPatchDocument.AppendAdd(patchModel.Path, false);
                                                    azureJsonPatchDocument.AppendAdd("/control_open_popup", OpenPopupControlModel.GetControlModel(responseModel));
                                                    await digitalTwinsClient.UpdateDigitalTwinAsync(UR_COBOT_DIGITAL_TWIN_ID, azureJsonPatchDocument);
                                                    _logger.LogInformation($"{patchModel.Path} executed succesfully");
                                                }
                                                break;
                                            case "/control_power_on/RequestPayload/IsCommandRequested":
                                                if (patchModel.Value is true)
                                                {
                                                    _logger.LogInformation(rootObjectModel.Data.ModelId, patchModel.Path);
                                                    object requestPayload = new
                                                    {
                                                        Value = DateTime.Now.ToString(),
                                                    };
                                                    ResponseModel responseModel = await GetResponseModelAsync(UR_COBOT_DEVICE_ID, "PowerOnCommand", requestPayload);
                                                    JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
                                                    azureJsonPatchDocument.AppendAdd(patchModel.Path, false);
                                                    azureJsonPatchDocument.AppendAdd("/control_power_on", PowerOnControlModel.GetControlModel(responseModel));
                                                    await digitalTwinsClient.UpdateDigitalTwinAsync(UR_COBOT_DIGITAL_TWIN_ID, azureJsonPatchDocument);
                                                    _logger.LogInformation($"{patchModel.Path} executed succesfully");
                                                }
                                                break;
                                            case "/control_power_off/RequestPayload/IsCommandRequested":
                                                if (patchModel.Value is true)
                                                {
                                                    _logger.LogInformation(rootObjectModel.Data.ModelId, patchModel.Path);
                                                    object requestPayload = new
                                                    {
                                                        Value = DateTime.Now.ToString(),
                                                    };
                                                    ResponseModel responseModel = await GetResponseModelAsync(UR_COBOT_DEVICE_ID, "PowerOffCommand", requestPayload);
                                                    JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
                                                    azureJsonPatchDocument.AppendAdd(patchModel.Path, false);
                                                    azureJsonPatchDocument.AppendAdd("/control_power_off", PowerOffControlModel.GetControlModel(responseModel));
                                                    await digitalTwinsClient.UpdateDigitalTwinAsync(UR_COBOT_DIGITAL_TWIN_ID, azureJsonPatchDocument);
                                                    _logger.LogInformation($"{patchModel.Path} executed succesfully");
                                                }
                                                break;
                                            case "/control_close_popup/RequestPayload/IsCommandRequested":
                                                if (patchModel.Value is true)
                                                {
                                                    _logger.LogInformation(rootObjectModel.Data.ModelId, patchModel.Path);
                                                    object requestPayload = new
                                                    {
                                                        Value = DateTime.Now.ToString(),
                                                    };
                                                    ResponseModel responseModel = await GetResponseModelAsync(UR_COBOT_DEVICE_ID, "ClosePopupCommand", requestPayload);
                                                    JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
                                                    azureJsonPatchDocument.AppendAdd(patchModel.Path, false);
                                                    azureJsonPatchDocument.AppendAdd("/control_close_popup", ClosePopupControlModel.GetControlModel(responseModel));
                                                    await digitalTwinsClient.UpdateDigitalTwinAsync(UR_COBOT_DIGITAL_TWIN_ID, azureJsonPatchDocument);
                                                    _logger.LogInformation($"{patchModel.Path} executed succesfully");
                                                }
                                                break;
                                            case "/control_start_free_drive/RequestPayload/IsCommandRequested":
                                                if (patchModel.Value is true)
                                                {
                                                    _logger.LogInformation(rootObjectModel.Data.ModelId, patchModel.Path);
                                                    object requestPayload = new
                                                    {
                                                        Value = DateTime.Now.ToString(),
                                                    };
                                                    ResponseModel responseModel = await GetResponseModelAsync(UR_COBOT_DEVICE_ID, "StartFreeDriveModeCommand", requestPayload);
                                                    JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
                                                    azureJsonPatchDocument.AppendAdd(patchModel.Path, false);
                                                    azureJsonPatchDocument.AppendAdd("/control_start_free_drive", StartFreeDriveControlModel.GetControlModel(responseModel));
                                                    await digitalTwinsClient.UpdateDigitalTwinAsync(UR_COBOT_DIGITAL_TWIN_ID, azureJsonPatchDocument);
                                                    _logger.LogInformation($"{patchModel.Path} executed succesfully");
                                                }
                                                break;
                                            case "/control_stop_free_drive/RequestPayload/IsCommandRequested":
                                                if (patchModel.Value is true)
                                                {
                                                    _logger.LogInformation(rootObjectModel.Data.ModelId, patchModel.Path);
                                                    object requestPayload = new
                                                    {
                                                        Value = DateTime.Now.ToString(),
                                                    };
                                                    ResponseModel responseModel = await GetResponseModelAsync(UR_COBOT_DEVICE_ID, "StopFreeDriveModeCommand", requestPayload);
                                                    JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
                                                    azureJsonPatchDocument.AppendAdd(patchModel.Path, false);
                                                    azureJsonPatchDocument.AppendAdd("/control_stop_free_drive", StopFreeDriveControlModel.GetControlModel(responseModel));
                                                    await digitalTwinsClient.UpdateDigitalTwinAsync(UR_COBOT_DIGITAL_TWIN_ID, azureJsonPatchDocument);
                                                    _logger.LogInformation($"{patchModel.Path} executed succesfully");
                                                }
                                                break;
                                            case "/control_close_safety_popup/RequestPayload/IsCommandRequested":
                                                if (patchModel.Value is true)
                                                {
                                                    _logger.LogInformation(rootObjectModel.Data.ModelId, patchModel.Path);
                                                    object requestPayload = new
                                                    {
                                                        Value = DateTime.Now.ToString(),
                                                    };
                                                    ResponseModel responseModel = await GetResponseModelAsync(UR_COBOT_DEVICE_ID, "CloseSafetyPopupCommand", requestPayload);
                                                    JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
                                                    azureJsonPatchDocument.AppendAdd(patchModel.Path, false);
                                                    azureJsonPatchDocument.AppendAdd("/control_close_safety_popup", CloseSafetyPopupControlModel.GetControlModel(responseModel));
                                                    await digitalTwinsClient.UpdateDigitalTwinAsync(UR_COBOT_DIGITAL_TWIN_ID, azureJsonPatchDocument);
                                                    _logger.LogInformation($"{patchModel.Path} executed succesfully");
                                                }
                                                break;
                                            case "/control_unlock_protective_stop/RequestPayload/IsCommandRequested":
                                                if (patchModel.Value is true)
                                                {
                                                    _logger.LogInformation(rootObjectModel.Data.ModelId, patchModel.Path);
                                                    object requestPayload = new
                                                    {
                                                        Value = DateTime.Now.ToString(),
                                                    };
                                                    ResponseModel responseModel = await GetResponseModelAsync(UR_COBOT_DEVICE_ID, "UnlockProtectiveStopCommand", requestPayload);
                                                    JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
                                                    azureJsonPatchDocument.AppendAdd(patchModel.Path, false);
                                                    azureJsonPatchDocument.AppendAdd("/control_unlock_protective_stop", UnlockProtectiveStopControlModel.GetControlModel(responseModel));
                                                    await digitalTwinsClient.UpdateDigitalTwinAsync(UR_COBOT_DIGITAL_TWIN_ID, azureJsonPatchDocument);
                                                    _logger.LogInformation($"{patchModel.Path} executed succesfully");
                                                }
                                                break;
                                            default:
                                                break;
                                        }
                                        stopwatch.Stop();
                                        _logger.LogInformation($"elapsed {stopwatch.ElapsedMilliseconds}ms");
                                    }
                                    else 
                                    {
                                        _logger.LogInformation($"{rootObjectModel.Data.ModelId} has no commands");
                                    }
                                }
                                else
                                {
                                    _logger.LogError("Patch is empty");
                                    return;
                                }
                            }
                        }
                        else if (rootObjectModel.Data.ModelId.Equals("dtmi:com:physical_twins:factory:robotiq_gripper;1"))
                        {
                            if (patchModelList is not null)
                            {
                                if (patchModelList.Count >= 1)
                                {
                                    PatchModel? patchModel = patchModelList
                                        .Where(x => x is not null && x.Path is not null && x.Path.Contains("RequestPayload"))
                                        .FirstOrDefault();
                                    if (patchModel is not null)
                                    {
                                        switch (patchModel.Path)
                                        {
                                            case "/control_activate_gripper/RequestPayload/IsCommandRequested":
                                                if (patchModel.Value is true)
                                                {
                                                    _logger.LogInformation(rootObjectModel.Data.ModelId, patchModel.Path);
                                                    object requestPayload = new
                                                    {
                                                        Value = DateTime.Now.ToString(),
                                                    };
                                                    ResponseModel responseModel = await GetResponseModelAsync(ROBOTIQ_GRIPPER_DEVICE_ID, "ActivateGripperCommand", requestPayload);
                                                    JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
                                                    azureJsonPatchDocument.AppendAdd(patchModel.Path, false);
                                                    azureJsonPatchDocument.AppendAdd("/control_activate_gripper", ActivateGripperControlModel.GetControlModel(responseModel, stopwatch));
                                                    await digitalTwinsClient.UpdateDigitalTwinAsync(ROBOTIQ_GRIPPER_DIGITAL_TWIN_ID, azureJsonPatchDocument);
                                                    _logger.LogInformation($"{patchModel.Path} executed succesfully");
                                                }
                                                break;
                                            case "/control_open_gripper/RequestPayload/IsCommandRequested":
                                                if (patchModel.Value is true)
                                                {
                                                    _logger.LogInformation(rootObjectModel.Data.ModelId, patchModel.Path);
                                                    object requestPayload = new
                                                    {
                                                        Value = DateTime.Now.ToString(),
                                                    };
                                                    ResponseModel responseModel = await GetResponseModelAsync(ROBOTIQ_GRIPPER_DEVICE_ID, "OpenGripperCommand", requestPayload);
                                                    JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
                                                    azureJsonPatchDocument.AppendAdd(patchModel.Path, false);
                                                    azureJsonPatchDocument.AppendAdd("/control_open_gripper", OpenGripperControlModel.GetControlModel(responseModel, stopwatch));
                                                    await digitalTwinsClient.UpdateDigitalTwinAsync(ROBOTIQ_GRIPPER_DIGITAL_TWIN_ID, azureJsonPatchDocument);
                                                    _logger.LogInformation($"{patchModel.Path} executed succesfully");
                                                }
                                                break;
                                            case "/control_close_gripper/RequestPayload/IsCommandRequested":
                                                if (patchModel.Value is true)
                                                {
                                                    _logger.LogInformation(rootObjectModel.Data.ModelId, patchModel.Path);
                                                    object requestPayload = new
                                                    {
                                                        Value = DateTime.Now.ToString(),
                                                    };
                                                    ResponseModel responseModel = await GetResponseModelAsync(ROBOTIQ_GRIPPER_DEVICE_ID, "CloseGripperCommand", requestPayload);
                                                    JsonPatchDocument azureJsonPatchDocument = new JsonPatchDocument();
                                                    azureJsonPatchDocument.AppendAdd(patchModel.Path, false);
                                                    azureJsonPatchDocument.AppendAdd("/control_close_gripper", CloseGripperControlModel.GetControlModel(responseModel, stopwatch));
                                                    await digitalTwinsClient.UpdateDigitalTwinAsync(ROBOTIQ_GRIPPER_DIGITAL_TWIN_ID, azureJsonPatchDocument);
                                                    _logger.LogInformation($"{patchModel.Path} executed succesfully");
                                                }
                                                break;
                                            default:
                                                break;
                                        }
                                        stopwatch.Stop();
                                        _logger.LogInformation($"elapsed {stopwatch.ElapsedMilliseconds}ms");
                                    }
                                    else
                                    {
                                        _logger.LogInformation($"{rootObjectModel.Data.ModelId} has no commands");
                                    }
                                }
                                else
                                {
                                    _logger.LogError("Patch is empty");
                                    return;
                                }
                            }
                        }
                        else
                        {
                            _logger.LogError($"ModelId {rootObjectModel.Data.ModelId} is not valid");
                        }
                    }
                    else
                    {
                        _logger.LogError("RootObjectModel or Data is null");
                    }
                }
                else
                {
                    _logger.LogError("EventGridEvent or Data is null");
                }
            }
            catch (Exception ex)
            {
                _logger.LogInformation(ex.ToString());
            }
        }
        private async Task<ResponseModel> GetResponseModelAsync(string device, string command, object payload)
        {
            try
            {
                CloudToDeviceMethodResult cloudToDeviceMethodResult = await InvokeDeviceMethodAsync(device, command, payload);
                _logger.LogInformation(JsonConvert.SerializeObject(cloudToDeviceMethodResult));
                return ResponseModel.GetSuccessResponse(cloudToDeviceMethodResult);
            }
            catch (JsonReaderException jex)
            {
                _logger.LogError(jex.ToString());
                return new ResponseModel();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex.ToString());
                return ResponseModel.GetExceptionResponse(ex.ToString());
            }
        }
        private static async Task<CloudToDeviceMethodResult> InvokeDeviceMethodAsync(string device, string command, object payload)
        {
            ServiceClient serviceClient = ServiceClient.CreateFromConnectionString(AIOT_HUB_SERVICE_URL);
            CloudToDeviceMethod cloudToDeviceMethod = new CloudToDeviceMethod(command, TimeSpan.FromSeconds(30));
            cloudToDeviceMethod.SetPayloadJson(JsonConvert.SerializeObject(payload));
            CloudToDeviceMethodResult cloudToDeviceMethodResult = await serviceClient.InvokeDeviceMethodAsync(device, cloudToDeviceMethod);
            return cloudToDeviceMethodResult;
        }
    }
}
