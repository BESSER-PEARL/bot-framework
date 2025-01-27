from typing import Any

from besser.agent.core.attribute import Attribute
from besser.agent.core.image.image_property import ImageProperty
from besser.agent.core.scenario.scenario_requirement import ScenarioRequirement
from besser.agent.core.session import Session
from besser.agent.cv.prediction.image_prediction import ImagePropertyPrediction


class ScenarioImagePropertyAttribute(Attribute):

    dictionary = {
        'score': float,
    }

    def __init__(self, name: str, value: Any):
        if name not in ScenarioImagePropertyAttribute.dictionary:
            raise ValueError(f"'{name}' is not a valid ScenarioImagePropertyAttribute. Allowed attributes are:\n{ScenarioImagePropertyAttribute.dictionary}")
        if ScenarioImagePropertyAttribute.dictionary[name] != type(value):
            raise ValueError(f"'{name}' ScenarioImagePropertyAttribute must be of type '{ScenarioImagePropertyAttribute.dictionary[name]}',not '{value}'")
        super().__init__(name, value)


class ScenarioImageProperty(ScenarioRequirement):

    def __init__(
            self,
            name: str,
            image_property: ImageProperty,
            attributes: dict[str, Any]
    ):

        super().__init__(name)
        self.image_property: ImageProperty = image_property
        self.attributes: list[ScenarioImagePropertyAttribute] = []
        for attr_name, attr_value in attributes.items():
            self.attributes.append(ScenarioImagePropertyAttribute(attr_name, attr_value))
        if 'score' not in [attribute.name for attribute in self.attributes]:
            raise ValueError(f"Please, provide the 'score' attribute for '{name}'")

    def get_attribute_value(self, name: str) -> Any:
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute.value
        return None

    def evaluate(self, session: Session):
        if session.image_prediction is None:
            return False
        image_property_predictions: list[ImagePropertyPrediction] = session.image_prediction.image_property_predictions
        score = self.get_attribute_value('score')
        for image_property_prediction in image_property_predictions:
            if image_property_prediction.image_property == self.image_property and image_property_prediction.score >= score:
                return True
        return False
