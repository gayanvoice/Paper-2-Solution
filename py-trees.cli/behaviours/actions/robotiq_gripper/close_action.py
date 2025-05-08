import argparse
import atexit
import multiprocessing
import multiprocessing.connection
import time
import typing
import py_trees

class CloseAction(py_trees.behaviour.Behaviour):
    def __init__(self, robotiq_gripper_twin_controller, name: str = "Close Action"):
        super(CloseAction, self).__init__(name)
        self.robotiq_gripper_twin_controller = robotiq_gripper_twin_controller
        self.logger.debug("%s.__init__()" % (self.__class__.__name__))

    def setup(self, **kwargs: int) -> None:
        self.logger.debug("%s.setup()->connections to an external process" % (self.__class__.__name__))
        self.parent_connection, self.child_connection = multiprocessing.Pipe()
        self.executing = multiprocessing.Process(target=self.robotiq_gripper_twin_controller.close, args=(self.child_connection,))
        atexit.register(self.executing.terminate)
        self.executing.start()

    def initialise(self) -> None:
        self.logger.debug("%s.initialise()->sending new goal" % (self.__class__.__name__))
        self.parent_connection.send(["new goal"])
        self.percentage_completion = 0

    def update(self) -> py_trees.common.Status:
        new_status = py_trees.common.Status.RUNNING
        if self.parent_connection.poll():
            self.percentage_completion, response_model = self.parent_connection.recv()
            self.feedback_message = response_model
            if self.percentage_completion == 100:
                if response_model.Status:
                    new_status = py_trees.common.Status.SUCCESS
                else: 
                    new_status = py_trees.common.Status.FAILURE
                
        if new_status == py_trees.common.Status.SUCCESS:
            self.logger.debug("%s.update()[%s->%s][%s]" % (self.__class__.__name__, self.status, new_status, self.feedback_message,)
            )
        else:
            self.feedback_message = "{0}%".format(self.percentage_completion)
            self.logger.debug("%s.update()[%s][%s]" % (self.__class__.__name__, self.status, self.feedback_message))
        return new_status

    def terminate(self, new_status: py_trees.common.Status) -> None:
        self.logger.debug("%s.terminate()[%s->%s]" % (self.__class__.__name__, self.status, new_status))
