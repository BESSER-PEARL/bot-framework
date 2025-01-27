from abc import ABC
from typing import Any


class Attribute(ABC):

    def __init__(self, name: str, value: Any):
        self.name: str = name
        self.value: str = value
