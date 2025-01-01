import base64
from typing import List

from mcp.types import *


class ResultGuard:
    MAX_SIZE_BYTES = 2 ** 20  # 1MB limit, Claude Desktop Client requirement

    @staticmethod
    def measure_size(contents: List[TextContent | ImageContent]) -> int:
        """
        Measure the total size of the given contents.

        Args:
            contents (List[TextContent | ImageContent]): List of text or image content.

        Returns:
            int: Total size of the contents in bytes.
        """
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
        """
        Validate the result by checking if the total size of the contents exceeds the maximum allowed size.

        Args:
            contents (List[TextContent | ImageContent]): List of text or image content.
            tool_name (str): Name of the tool that generated the result.
            arguments (dict[str, Any] | None): Arguments used by the tool.

        Returns:
            List[TextContent | ImageContent]: Original contents if the size is within the limit, otherwise a message indicating the size is too large.
        """
        size = self.measure_size(contents)
        if size > self.MAX_SIZE_BYTES:
            return [TextContent(
                type="text",
                text=f"Result for tool {tool_name} with arguments {arguments} is too large: {size} bytes"
            )]
        return contents
