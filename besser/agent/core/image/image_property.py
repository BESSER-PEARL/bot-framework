from typing import Any

from besser.agent.core.attribute import Attribute
from besser.agent.core.image.image_requirement import ImageRequirement


class ImagePropertyAttribute(Attribute):

    dictionary = {
        'description': str,
    }

    def __init__(self, name: str, value: Any):
        if name not in ImagePropertyAttribute.dictionary:
            raise ValueError(f"'{name}' is not a valid ImagePropertyAttribute. Allowed attributes are:\n{ImagePropertyAttribute.dictionary}")
        if ImagePropertyAttribute.dictionary[name] != type(value):
            raise ValueError(f"'{name}' ImagePropertyAttribute must be of type '{ImagePropertyAttribute.dictionary[name]}',not '{value}'")
        super().__init__(name, value)


class ImageProperty(ImageRequirement):
    """The Image Property core component of an agent.

    Image Properties are used to specify the properties that can be detected by the agent in an image.

    Args:
        name (str): the image property's name

    Attributes:
        name (str): The image property's name
    """

    def __init__(self, name: str, attributes: dict[str, Any] = {}):
        super().__init__(name)
        self.attributes: list[ImagePropertyAttribute] = []
        for attr_name, attr_value in attributes.items():
            self.attributes.append(ImagePropertyAttribute(attr_name, attr_value))

    def has_attribute(self, name: str) -> bool:
        for attribute in self.attributes:
            if attribute.name == name:
                return True

    def get_attribute_value(self, name: str) -> Any:
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute.value
        return None
