import asyncio
import uuid6
import logging

from core.core_ui import CoreUi
from core.core_queue import CoreQueue
from core.gom import GOM
from core.ur_cobot import URCobot
from core.robotiq_gripper import RobotiqGripper

async def main():
    client_cli_session_uuid = uuid6.uuid8()
    logging.basicConfig(filename='local-iothub-cli-log.log', filemode='w', level=logging.DEBUG,
                        format=f"%(asctime)s - {client_cli_session_uuid} - %(levelname)s - %(name)s  - %(message)s")
    CoreUi.welcome(client_cli_session_uuid=client_cli_session_uuid)
    try:
        queue = asyncio.Queue()
        core_queue = CoreQueue()
        ur_cobot = URCobot(client_cli_session_uuid=client_cli_session_uuid)
        robotiq_gripper = RobotiqGripper(client_cli_session_uuid=client_cli_session_uuid)
        await asyncio.gather(core_queue.listen(queue),
                             robotiq_gripper.connect_azure_iot(queue),
                             ur_cobot.connect_azure_iot(queue))
    except asyncio.exceptions.CancelledError:
        logging.error("The execution of the thread was manually stopped due to a KeyboardInterrupt signal.")
    except SystemExit:
        logging.error("local iothub cli was stopped.")


if __name__ == '__main__':
    asyncio.run(main())
