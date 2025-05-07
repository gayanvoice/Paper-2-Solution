import argparse
import atexit
import multiprocessing
import multiprocessing.connection
import time
import typing

import py_trees.common
import py_trees.console as console

class ActionBehaviour(py_trees.behaviour.Behaviour):
    def __init__(self, name: str):
        super(ActionBehaviour, self).__init__(name)
        self.logger.debug("%s.__init__()" % (self.__class__.__name__))

    def setup(self, **kwargs: int) -> None:
        self.logger.debug("%s.setup()->connections to an external process" % (self.__class__.__name__))
        self.parent_connection, self.child_connection = multiprocessing.Pipe()
        self.planning = multiprocessing.Process(target=self.execute_process, args=(self.child_connection,))
        atexit.register(self.planning.terminate)
        self.planning.start()

    def initialise(self) -> None:
        self.logger.debug("%s.initialise()->sending new goal" % (self.__class__.__name__))
        self.parent_connection.send(["new goal"])
        self.percentage_completion = 0

    def update(self) -> py_trees.common.Status:
        new_status = py_trees.common.Status.RUNNING
        if self.parent_connection.poll():
            self.percentage_completion = self.parent_connection.recv().pop()
            if self.percentage_completion == 100:
                new_status = py_trees.common.Status.SUCCESS
        if new_status == py_trees.common.Status.SUCCESS:
            self.feedback_message = "Processing finished"
            self.logger.debug(
                "%s.update()[%s->%s][%s]"
                % (
                    self.__class__.__name__,
                    self.status,
                    new_status,
                    self.feedback_message,
                )
            )
        else:
            self.feedback_message = "{0}%".format(self.percentage_completion)
            self.logger.debug(
                "%s.update()[%s][%s]"
                % (self.__class__.__name__, self.status, self.feedback_message)
            )
        return new_status

    def terminate(self, new_status: py_trees.common.Status) -> None:
        """Nothing to clean up in this example."""
        self.logger.debug(
            "%s.terminate()[%s->%s]"
            % (self.__class__.__name__, self.status, new_status)
        )

    @staticmethod
    def execute_process(pipe_connection: multiprocessing.connection.Connection) -> None:
        idle = True
        percentage_complete = 0
        try:
            while True:
                if pipe_connection.poll():
                    pipe_connection.recv()
                    percentage_complete = 0
                    idle = False
                if not idle:
                    percentage_complete += 10
                    pipe_connection.send([percentage_complete])
                    if percentage_complete == 100:
                        idle = True
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
