import multiprocessing
import sys
import time
import py_trees


from azure.identity import InteractiveBrowserCredential
from azure.digitaltwins.core import DigitalTwinsClient

from ActionBehaviour import ActionBehaviour
from behaviours.actions.robotiq_gripper.activate_action import ActivateAction
from behaviours.actions.robotiq_gripper.open_action import OpenAction
from behaviours.actions.robotiq_gripper.close_action import CloseAction

from model.robotiq_gripper_twin_model import RobotiqGripperTwinModel
from model.ur_cobot_twin_model import URCobotTwinModel

from controller.robotiq_gripper_twin_controller import RobotiqGripperTwinController
from controller.ur_cobot_twin_controller import URCobotTwinController

def main() -> None:
    tenent_id = "c263ac0d-270a-43fd-95d1-e279d1002ff9";
    digital_twins_url = "https://paper-2-adt-1.api.uks.digitaltwins.azure.net/";
    robotiq_gripper_twin_id = "robotiq_gripper";
    ur_cobot_twin_id = "ur_cobot";

    interactive_browser_credential = InteractiveBrowserCredential(tenant_id=tenent_id)
    digital_twins_client = DigitalTwinsClient(digital_twins_url, interactive_browser_credential)

    robotiq_gripper_twin_controller = RobotiqGripperTwinController(digital_twins_client, robotiq_gripper_twin_id)
    ur_cobot_twin_controller = URCobotTwinController(digital_twins_client, ur_cobot_twin_id)
    
    robotiq_gripper_twin_model = robotiq_gripper_twin_controller.get_digital_twin()

    py_trees.logging.level = py_trees.logging.Level.DEBUG

    activate_action = ActivateAction(robotiq_gripper_twin_controller = robotiq_gripper_twin_controller)
    open_action = OpenAction(robotiq_gripper_twin_controller = robotiq_gripper_twin_controller)
    close_action = CloseAction(robotiq_gripper_twin_controller = robotiq_gripper_twin_controller)

    # close_action.setup()

    root = py_trees.composites.Sequence(name="Sequence", memory=True)
    root.add_child(activate_action)
    root.add_child(open_action)
    root.add_child(close_action)
    root.setup_with_descendants()

    for _unused_i in range(0, 100):
        root.tick_once()
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
