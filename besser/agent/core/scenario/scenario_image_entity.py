from typing import Any

from besser.agent.core.attribute import Attribute
from besser.agent.core.image.image_entity import ImageEntity
from besser.agent.core.scenario.scenario_requirement import ScenarioRequirement
from besser.agent.core.session import Session
from besser.agent.cv.prediction.image_prediction import ImageObjectPrediction


class ScenarioImageEntityAttribute(Attribute):

    dictionary = {
        'score': float,
        'min': int,
        'max': int,
    }

    def __init__(self, name: str, value: Any):
        if name not in ScenarioImageEntityAttribute.dictionary:
            raise ValueError(
                f"'{name}' is not a valid ScenarioImageEntityAttribute. Allowed attributes are:\n{ScenarioImageEntityAttribute.dictionary}")
        if ScenarioImageEntityAttribute.dictionary[name] != type(value):
            raise ValueError(
                f"'{name}' ScenarioImageEntityAttribute must be of type '{ScenarioImageEntityAttribute.dictionary[name]}',not '{value}'")
        super().__init__(name, value)


class ScenarioImageEntity(ScenarioRequirement):

    def __init__(
            self,
            name: str,
            image_entity: ImageEntity,
            attributes: dict[str, Any]
    ):

        super().__init__(name)
        self.image_entity: ImageEntity = image_entity
        self.attributes: list[ScenarioImageEntityAttribute] = []
        for attr_name, attr_value in attributes.items():
            self.attributes.append(ScenarioImageEntityAttribute(attr_name, attr_value))
        if 'score' not in [attribute.name for attribute in self.attributes]:
            raise ValueError(f"Please, provide the 'score' attribute for '{name}'")
        if 'min' not in [attribute.name for attribute in self.attributes]:
            self.attributes.append(ScenarioImageEntityAttribute('min', 1))
        if 'max' not in [attribute.name for attribute in self.attributes]:
            self.attributes.append(ScenarioImageEntityAttribute('max', 0))
        min = self.get_attribute_value('min')
        max = self.get_attribute_value('max')
        if min < 1:
            raise ValueError(f'Error creating {self.name}: min must be > 0')
        if min > max and max != 0:
            raise ValueError(f'Error creating {self.name}: min must <= max (unless max = 0)')

    def get_attribute_value(self, name: str) -> Any:
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute.value
        return None

    def evaluate(self, session: Session):
        if session.image_prediction is None:
            return False
        _min = self.get_attribute_value('min')
        _max = self.get_attribute_value('max')
        score = self.get_attribute_value('score')
        image_object_predictions: list[ImageObjectPrediction] = session.image_prediction.image_object_predictions
        filtered_image_object_predictions = [
            image_object_prediction for image_object_prediction in image_object_predictions
            if image_object_prediction.image_entity == self.image_entity and image_object_prediction.score >= score
        ]
        num_predictions = len(filtered_image_object_predictions)
        if num_predictions == 0:
            return False
        if _min == 0 and _max == 0:
            return True
        if _min == 0 and num_predictions <= _max:
            return True
        if _max == 0 and num_predictions >= _min:
            return True
        if _min <= num_predictions <= _max:
            return True
        return False
