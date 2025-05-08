import json
import re
from typing import List
import uuid

import py_trees
from py_trees import behaviour
from py_trees.composites import Selector, Sequence

from behaviours.actions.robotiq_gripper.activate_action import ActivateAction
from behaviours.actions.robotiq_gripper.close_action import CloseAction
from behaviours.actions.robotiq_gripper.open_action import OpenAction

from behaviours.checks.temperature_check import TemperatureCheck
from helpers.llm_helper import LlmHelper
from models.llm.conditional_llm_request_model import ConditionalLlmRequestModel
from models.llm.sequence_llm_request_model import SequenceLlmRequestModel

class DynamicBehaviourTreeController:
    def __init__(self, digital_twin_controller):
        super(DynamicBehaviourTreeController, self).__init__()
        self._digital_twin_controller = digital_twin_controller
        self._behaviour_map = {
            "activate_gripper": ActivateAction,
            "open_gripper": OpenAction,
            "close_gripper": CloseAction
        }

    def create_sequence_composite(self, json_str: str) -> Sequence:
        if self._is_sequence_statement(json_str):
            data = json.loads(json_str)
            sequence_llm_request_model = SequenceLlmRequestModel(action_sequence=data["sequence"])
            actions = self._get_actions(sequence_llm_request_model.action_sequence)
            sequence = Sequence(name=str(uuid.uuid4()), memory=True)
            sequence.add_children(actions)
            return sequence
        else:
            return None

    def create_selector_composite(self, json_str: str) -> Sequence:
        if self.is_selector_statement(json_str):
            data = json.loads(json_str)
            conditional_llm_request_model = ConditionalLlmRequestModel(
                if_check=data["if"],
                then_actions=data["then"],
                else_actions=data["else"]
            )

            if_check = self._get_check(conditional_llm_request_model.if_check)
            then_actions = self._get_actions(conditional_llm_request_model.then_actions)
            else_actions = self._get_actions(conditional_llm_request_model.else_actions)

            selector = Selector(name=str(uuid.uuid4()), memory=True)
            if_sequence = py_trees.composites.Sequence(name=str(uuid.uuid4()), memory=True)
            then_sequence = py_trees.composites.Sequence(name=str(uuid.uuid4()), memory=True)
            else_sequence = py_trees.composites.Sequence(name=str(uuid.uuid4()), memory=True)

            then_sequence.add_children(then_actions)
            else_sequence.add_children(else_actions)

            if_sequence.add_children([if_check, then_sequence])

            selector.add_children([if_sequence, else_sequence])

            return selector
        else:
            return None

    def _get_check(self, check: str):
        pattern = r"(\w+)\((.*?)\)"
        match = re.match(pattern, check)
        if match:
            behaviour_name = match.group(1)
            behaviour_parameters = match.group(2)
            if behaviour_name == "temperature_check":
                condition, required_temperature, recorded_temperature = behaviour_parameters.split(",")
                return TemperatureCheck(condition, required_temperature, recorded_temperature, str(uuid.uuid4()))

    def _get_actions(self, actions: List[str]):
        behaviour_sequence = []
        for action in actions:
                pattern = r"(\w+)\((.*?)\)"
                match = re.match(pattern, action)
                if match:
                    action_name = match.group(1)
                    action_parameters = match.group(2)
                    if action_name in self._behaviour_map:
                        behaviour_sequence.append(self._behaviour_map[action_name](self._digital_twin_controller, str(uuid.uuid4())))
        return behaviour_sequence

    def _is_sequence_statement(self, json_str: str) -> bool:
        try:
            data = json.loads(json_str)
            return isinstance(data.get("sequence"), list) and \
                   all(isinstance(action, str) for action in data["sequence"])
        except (json.JSONDecodeError, KeyError):
            return False

    def is_selector_statement(self, json_str: str) -> bool:
        try:
            data = json.loads(json_str)
            if "if" in data and "then" in data and "else" in data:
                if isinstance(data["then"], list) and isinstance(data["else"], list):
                    if all(isinstance(action, str) for action in data["then"]) and all(isinstance(action, str) for action in data["else"]):
                        return True
            return False
        except json.JSONDecodeError:
            return False
        