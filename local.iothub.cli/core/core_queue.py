import asyncio
from core import core_global


class CoreQueue:
    @staticmethod
    def stdin_listener():
        while True:
            core_global.is_queue_running = True
            selection = input("Press Q to quit Local IoT Hub CLI:")
            if selection == "Q" or selection == "q":
                core_global.is_queue_running = False
                break

    async def listen(self, queue):
        loop = asyncio.get_running_loop()
        user_finished = loop.run_in_executor(None, self.stdin_listener)
        await user_finished
        await queue.put(None)
