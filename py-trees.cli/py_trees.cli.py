import multiprocessing
import sys
import time
import py_trees
import json

from azure.identity import InteractiveBrowserCredential
from azure.digitaltwins.core import DigitalTwinsClient

from behaviours.actions.robotiq_gripper.activate_action import ActivateAction
from behaviours.actions.robotiq_gripper.open_action import OpenAction
from behaviours.actions.robotiq_gripper.close_action import CloseAction

from behaviours.checks.temperature_check import TemperatureCheck

from controllers.behaviour_trees.dynamic_behaviour_tree_controller import DynamicBehaviourTreeController
from helpers.llm_helper import LlmHelper
from models.digital_twins.robotiq_gripper_digital_twin_model import RobotiqGripperDigitalTwinModel
from models.digital_twins.ur_cobot_digital_twin_model import URCobotDigitalTwinModel

from controllers.digital_twins.robotiq_gripper_digital_twin_controller import RobotiqGripperDigitalTwinController
from controllers.digital_twins.ur_cobot_digital_twin_controller import URCobotTwinController

from models.llm.conditional_llm_request_model import ConditionalLlmRequestModel
from models.llm.sequence_llm_request_model import SequenceLlmRequestModel

def main() -> None:
    tenent_id = "c263ac0d-270a-43fd-95d1-e279d1002ff9";
    digital_twins_url = "https://paper-2-adt-1.api.uks.digitaltwins.azure.net/";
    robotiq_gripper_twin_id = "robotiq_gripper";
    ur_cobot_twin_id = "ur_cobot";

    interactive_browser_credential = InteractiveBrowserCredential(tenant_id=tenent_id)
    digital_twins_client = DigitalTwinsClient(digital_twins_url, interactive_browser_credential)

    robotiq_gripper_twin_controller = RobotiqGripperDigitalTwinController(digital_twins_client, robotiq_gripper_twin_id)
    ur_cobot_twin_controller = URCobotTwinController(digital_twins_client, ur_cobot_twin_id)
    
    robotiq_gripper_twin_model = robotiq_gripper_twin_controller.get_digital_twin()

    py_trees.logging.level = py_trees.logging.Level.DEBUG

    # activate_action_1 = ActivateAction(robotiq_gripper_twin_controller = robotiq_gripper_twin_controller)
    # activate_action_2 = ActivateAction(robotiq_gripper_twin_controller = robotiq_gripper_twin_controller)
    # open_action = OpenAction(robotiq_gripper_twin_controller = robotiq_gripper_twin_controller)
    # close_action = CloseAction(robotiq_gripper_twin_controller = robotiq_gripper_twin_controller)

    # temperature_check = TemperatureCheck("equal_to", 20, 20)

    # csv_seq_str = "activate_gripper(), open_gripper(), close_gripper()"

    json_str = '''
    {
        "if": "temperature_check(equal_to, 20, 19)",
        "then": ["activate_gripper()", "close_gripper()"],
        "else": ["activate_gripper()", "open_gripper()"]
    }
    '''

    # result = LlmHelper.is_if_else_statement(json_str)
    # print(result)
    
    # result = LlmHelper.is_sequence_statement(json_str)
    # print(result)

    # data = json.loads(json_str)

    # conditional_request_model = ConditionalLlmRequestModel(
    #     if_check=data["if"],
    #     then_actions=data["then"],
    #     else_actions=data["else"]
    # )

    # print(conditional_request_model)

    # selector = py_trees.composites.Selector("If Selector", memory=True)

    # if_sequence_branch = py_trees.composites.Sequence(name="Then Sequence", memory=True)
    # if_sequence_branch.add_children([activate_action_1, close_action])

    # if_sequence = py_trees.composites.Sequence("If Block", memory=True)
    # if_sequence.add_children([temperature_check, if_sequence_branch])

    # else_sequence_branch = py_trees.composites.Sequence(name="Else Sequence", memory=True)
    # else_sequence_branch.add_children([activate_action_2, open_action])

    # selector.add_children([if_sequence, else_sequence_branch])

    # selector.setup_with_descendants()


    # root = py_trees.composites.Selector("If Else", memory=True)
    # condition = temperature_check
    # if_branch = close_action
    # else_branch = open_action

    # if_sequence = py_trees.composites.Sequence("If Block", memory=True)
    # if_sequence.add_children([condition, if_branch])

    # root.add_children([if_sequence, else_branch])
    # root.setup_with_descendants()


    # json_str = '''
    # {
    #     "sequence": [ "activate_gripper()", "open_gripper()", "close_gripper()", "activate_gripper()" ]
    # }
    # '''

    # result = LlmHelper.is_if_else_statement(json_str)
    # print(result)

    # result = LlmHelper.is_sequence_statement(json_str)
    # print(result)

    # data = json.loads(json_str)

    # sequence_request_model = SequenceLlmRequestModel(
    #     sequence_actions=data["sequence"]
    # )

    # print(sequence_request_model)

    # class_map = {
    #     "activate_gripper": ActivateAction,
    #     "open_gripper": OpenAction,
    #     "close_gripper": CloseAction
    # }




    # action_map = {
    #     name: cls(robotiq_gripper_twin_controller)
    #     for name, cls in class_map.items()
    #     if name + "()" in sequence_request_model.sequence_actions
    # }

    # root = py_trees.composites.Sequence(name="Sequence", memory=True)
    # for name, instance in action_map.items():
    #    root.add_child(instance)


    # root.setup_with_descendants()

    core_behaviour_tree_controller = DynamicBehaviourTreeController(robotiq_gripper_twin_controller)
    selector = core_behaviour_tree_controller.create_selector_composite(json_str)
    # selector = core_behaviour_tree_controller.create_sequence_composite(json_str)
    selector.setup_with_descendants()



    while True:
        if selector.status == py_trees.common.Status.SUCCESS:
            print("Tree completed successfully.")
            break
        selector.tick_once()
        time.sleep(1)
    print("\n")



    # move_response = ur_cobot_twin_controller.move(-127, -100, -130, -40, 96, -7)
    # print(move_response)

    # time.sleep(2)

    # move_response = ur_cobot_twin_controller.move(127, 100, 130, 40, -96, 7)
    # print(move_response)

    # time.sleep(2)

    # open_popup_response = ur_cobot_twin_controller.open_popup("some text")
    # print(open_popup_response)

    # time.sleep(2)

    # close_popup_response = ur_cobot_twin_controller.close_popup()
    # print(close_popup_response)


    # time.sleep(2)

    # start_free_drive_response = ur_cobot_twin_controller.start_free_drive()
    # print(start_free_drive_response)

    # time.sleep(2)

    # stop_free_drive_response = ur_cobot_twin_controller.stop_free_drive()
    # print(stop_free_drive_response)

    # time.sleep(2)

    # power_off_response = ur_cobot_twin_controller.power_off()
    # print(power_off_response)

    # time.sleep(2)

    # power_on_response = ur_cobot_twin_controller.power_on()
    # print(power_on_response)


    # py_trees.logging.level = py_trees.logging.Level.DEBUG

    # root = py_trees.composites.Sequence(name="Sequence", memory=True)





    # for action in ["Action 1", "Action 2", "Action 3"]:
    #     rssss = py_trees.behaviours.StatusQueue(
    #         name=action,
    #         queue=[
    #             py_trees.common.Status.RUNNING,
    #             py_trees.common.Status.SUCCESS,
    #         ],
    #         eventually=py_trees.common.Status.SUCCESS,
    #     )
    #     root.add_child(rssss)

    # py_trees.display.render_dot_tree(root)
    # sys.exit()

    # root.setup_with_descendants()

    # for i in range(1, 6):
    #     try:
    #         print("\n--------- Tick {0} ---------\n".format(i))
    #         root.tick_once()
    #         print("\n")
    #         print(py_trees.display.unicode_tree(root=root, show_status=True))
    #         time.sleep(1.0)
    #     except KeyboardInterrupt:
    #         break
    # print("\n")



    # actionBehaviour = ActionBehaviour(name="Action")
    # actionBehaviour.setup()
    # try:
    #     for _unused_i in range(0, 12):
    #         actionBehaviour.tick_once()
    #         time.sleep(0.5)
    #     print("\n")
    # except KeyboardInterrupt:
    #     pass

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
