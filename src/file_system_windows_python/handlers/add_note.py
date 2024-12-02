import logging

from mcp.types import TextContent

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.util.path_validator import PathValidator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AddNoteHandler(Handler):
    async def execute(self, arguments: dict) -> list[TextContent]:
        logger.debug("Starting add note handler")

        if not arguments:
            raise ValueError("Missing arguments")
        note_name = arguments.get("name")
        if not note_name:
            raise ValueError("Missing tool name")
        content = arguments.get("content")
        if not content:
            raise ValueError("Missing tool content")

        await PathValidator.validate_path(note_name)
        logger.debug("Path validation passed")

        return [
            TextContent(
                type="text",
                text=f"Added the note {note_name} with content: {content}",
            )
        ]
