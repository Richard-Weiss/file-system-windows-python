import logging

from mcp.types import TextContent

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.util.config import Config
from file_system_windows_python.util.logging import log_execution

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ListDeniedDirectoriesHandler(Handler):
    """
    Handler for listing denied directories.

    This handler retrieves the list of denied directories from the configuration
    and returns it as a list of TextContent objects.
    """

    @log_execution("list_denied_directories")
    async def execute(self, arguments: None) -> list[TextContent]:
        """
        Execute the handler to list denied directories.

        Args:
            arguments None: A dictionary of arguments or None.

        Returns:
            list[TextContent]: A list of TextContent objects representing the denied directories.
        """
        text_content_list = []
        for denied_path in Config().deny:
            text_content_list.append(
                TextContent(
                    type="text",
                    text=f"Denied path: {denied_path}",
                )
            )
        if not text_content_list:
            text_content_list.append(
                TextContent(
                    type="text",
                    text=f"No denied paths. Let's goooooo!",
                )
            )

        return text_content_list
