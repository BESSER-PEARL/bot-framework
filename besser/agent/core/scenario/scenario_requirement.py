from abc import ABC, abstractmethod

from besser.agent.core.scenario.expression import Expression
from besser.agent.core.session import Session


class ScenarioRequirement(Expression):

    def __init__(self, name: str):
        super().__init__()
        self.name: str = name

    def __str__(self):
        return self.name
