from enum import Enum
from typing import Any

from besser.agent.core.attribute import Attribute
from besser.agent.core.image.image_requirement import ImageRequirement


class ImageEntityAttribute(Attribute):

    dictionary = {
        'description': str,
    }

    def __init__(self, name: str, value: Any):
        if name not in ImageEntityAttribute.dictionary:
            raise ValueError(f"'{name}' is not a valid ImageEntityAttribute. Allowed attributes are:\n{ImageEntityAttribute.dictionary}")
        if ImageEntityAttribute.dictionary[name] != type(value):
            raise ValueError(f"'{name}' ImageEntityAttribute must be of type '{ImageEntityAttribute.dictionary[name]}',not '{value}'")
        super().__init__(name, value)


class ImageEntity(ImageRequirement):
    """The Image Entity core component of an agent.

    Image Entities are used to specify the entities that can be detected by the agent in an image.

    Args:
        name (str): the image entity's name

    Attributes:
        name (str): The image entity's name
    """

    def __init__(self, name: str, attributes: dict[str, Any] = {}):
        super().__init__(name)
        self.attributes: list[ImageEntityAttribute] = []
        for attr_name, attr_value in attributes.items():
            self.attributes.append(ImageEntityAttribute(attr_name, attr_value))

    def get_attribute_value(self, name: str) -> Any:
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute.value
        return None
