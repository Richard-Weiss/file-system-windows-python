from abc import ABC, abstractmethod

from mcp.types import *


class Handler(ABC):
    """
    Abstract class for all handlers.

    This class serves as an interface for all handler classes.
    It enforces the implementation of the `execute` method in any subclass.
    """

    @abstractmethod
    async def execute(self, arguments: dict | None) -> list[TextContent | ImageContent | EmbeddedResource]:
        """
        Abstract method to be implemented by subclasses.

        Args:
            arguments (dict | None): A dictionary of arguments or None.

        Returns:
            list[TextContent | ImageContent | EmbeddedResource]: A list of content objects.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError()
