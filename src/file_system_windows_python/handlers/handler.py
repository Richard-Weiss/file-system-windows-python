from abc import ABC, abstractmethod
from mcp.types import *


class Handler(ABC):
    @abstractmethod
    async def execute(self, arguments: dict) \
            -> list[TextContent | ImageContent | EmbeddedResource]:
        raise NotImplementedError()
