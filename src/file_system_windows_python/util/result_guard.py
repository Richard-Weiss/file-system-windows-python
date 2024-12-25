import base64
from typing import List

from mcp.types import *


class ResultGuard:
    MAX_SIZE_BYTES = 2 ** 20  # 1MB limit, Claude Desktop Client requirement

    @staticmethod
    def measure_size(contents: List[TextContent | ImageContent]) -> int:
        content_bytes = 0
        for content in contents:
            if isinstance(content, TextContent):
                content_bytes += len(content.text.encode('utf-8'))
            elif isinstance(content, ImageContent):
                content_bytes += len(base64.b64decode(content.data))
        return content_bytes

    def validate_result(
            self,
            contents: List[TextContent | ImageContent],
            tool_name: str,
            arguments: dict[str, Any] | None) -> List[TextContent | ImageContent]:
        size = self.measure_size(contents)
        if size > self.MAX_SIZE_BYTES:
            return [TextContent(
                type="text",
                text=f"Result for tool {tool_name} with arguments {arguments} is too large: {size} bytes"
            )]
        return contents
