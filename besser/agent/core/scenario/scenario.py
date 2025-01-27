from enum import Enum
from typing import Union

from besser.agent.core.scenario.boolean_expression import BooleanExpression, BooleanOperator
from besser.agent.core.scenario.expression import Expression
from besser.agent.core.scenario.scenario_requirement import ScenarioRequirement
from besser.agent.core.session import Session





class Scenario:

    def __init__(self, name: str):
        self.name: str = name
        self.expression: BooleanExpression = None

    def __str__(self):
        return self.expression.__str__()

    def set_expression(self, expression: Expression) -> None:
        self.expression = expression

    def evaluate(self, session: Session) -> bool:
        return self.expression.evaluate(session)


