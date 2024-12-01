from mcp.types import TextContent

from file_system_windows_python.util.config import Config
from file_system_windows_python.handlers.handler import Handler


class AddNoteHandler(Handler):
    async def execute(self, arguments: dict) -> list[TextContent]:
        note_name = arguments.get("name")
        if not note_name:
            raise ValueError("Missing tool name")
        content = arguments.get("content")
        if not content:
            raise ValueError("Missing tool content")

        return [
            TextContent(
                type="text",
                text=f"Added note '{note_name}' with content: {Config().allow}, {Config().deny}",
            )
        ]
