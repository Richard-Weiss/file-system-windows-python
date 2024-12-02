import logging

from mcp.types import TextContent

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.util.config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ListDeniedDirectoriesHandler(Handler):
    async def execute(self, arguments: dict | None) -> list[TextContent]:

        logger.debug("Executing list_denied_directories handler")

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
