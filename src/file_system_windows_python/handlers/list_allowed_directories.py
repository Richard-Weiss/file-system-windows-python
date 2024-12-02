import logging

from mcp.types import TextContent

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.util.config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ListAllowedDirectoriesHandler(Handler):
    async def execute(self, arguments: dict | None) -> list[TextContent]:

        logger.debug("Executing list_allowed_directories handler")

        text_content_list = []
        for allowed_path in Config().allow:
            text_content_list.append(
                TextContent(
                    type="text",
                    text=f"Allowed path: {allowed_path}",
                )
            )

        return text_content_list
