import logging
from pathlib import Path

import aiofiles
from mcp.types import TextContent

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.util.path_validator import PathValidator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class WriteFileHandler(Handler):
    async def execute(self, arguments: dict | None) -> list[TextContent]:
        logger.debug("Executing write file handler")
        path = arguments.get("path")
        content: str = arguments.get("content")

        logger.debug("Content: %s", content)

        if not path:
            raise ValueError("Missing path")
        if not content:
            raise ValueError("Missing content")

        await PathValidator.validate_file_path(path)
        file_path = Path(path).resolve()

        logger.debug(f"Writing content to {file_path}")
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(content)
        logger.debug(f"Wrote content to {file_path}")

        return [
            TextContent(
                type="text",
                text=f"Successfully wrote {len(content)} characters to {path}"
            )
        ]
