from enum import Enum

from besser.agent.core.scenario.expression import Expression
from besser.agent.core.scenario.scenario_requirement import ScenarioRequirement
from besser.agent.core.session import Session


class BooleanOperator(Enum):
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'


class BooleanExpression(Expression):

    def __init__(self, operator: BooleanOperator, expressions: list[Expression]):
        # TODO: Run SAT solver to evaluate satisfiability of expression
        # Some libraries: pip install z3-solver, python-sat, pyminisat, pycosat
        # TODO: Convert to CNF? (OR conjunctions only)

        super().__init__()
        if operator in [BooleanOperator.AND, BooleanOperator.OR] and len(expressions) < 2:
            raise ValueError(f'Operator {operator} requires at least 2 expressions')
        if operator == BooleanOperator.NOT and len(expressions) != 1:
            raise ValueError(f'Operator {operator} requires 1 expression')
        self.operator: BooleanOperator = operator
        self.expressions: list[Expression] = expressions

    def __str__(self):
        return f'{self.operator}{[expression.__str__() for expression in self.expressions]}'

    def evaluate(self, session: Session) -> bool:
        if self.operator == BooleanOperator.AND:
            return all([expression.evaluate(session) for expression in self.expressions])
        if self.operator == BooleanOperator.OR:
            return any([expression.evaluate(session) for expression in self.expressions])
        if self.operator == BooleanOperator.NOT:
            return not self.expressions[0].evaluate(session)


def AND(expressions: list[Expression]) -> BooleanExpression:
    return BooleanExpression(operator=BooleanOperator.AND, expressions=expressions)


def OR(expressions: list[Expression]) -> BooleanExpression:
    return BooleanExpression(operator=BooleanOperator.OR, expressions=expressions)


def NOT(expression: Expression) -> BooleanExpression:
    return BooleanExpression(operator=BooleanOperator.NOT, expressions=[expression])
