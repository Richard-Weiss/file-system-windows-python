import logging

from mcp.types import TextContent

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.util.config import Config
from file_system_windows_python.util.logging import log_execution

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ListAllowedDirectoriesHandler(Handler):
    """
    Handler for listing allowed directories.

    This handler retrieves the list of allowed directories from the configuration
    and returns it as a list of TextContent objects.
    """

    @log_execution("list_allowed_directories")
    async def execute(self, arguments: None) -> list[TextContent]:
        """
        Execute the handler to list allowed directories.

        Args:
            arguments None: No arguments are expected.

        Returns:
            list[TextContent]: A list of TextContent objects representing the allowed directories.
        """
        text_content_list = []
        for allowed_path in Config().allow:
            text_content_list.append(
                TextContent(
                    type="text",
                    text=f"Allowed path: {allowed_path}",
                )
            )

        return text_content_list
