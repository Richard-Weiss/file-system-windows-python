import base64
import logging
from pathlib import Path

import aiofiles
from mcp.types import TextContent, ImageContent

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.util.path_validator import PathValidator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ReadFileHandler(Handler):
    async def execute(self, arguments: dict | None) -> list[TextContent | ImageContent]:
        logger.debug("Executing read file handler")
        path = arguments.get("path")
        if not path:
            raise ValueError("Missing path")
        await PathValidator.validate_file_path(path)

        file_path = Path(path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File {path} does not exist!")
        if not file_path.is_file():
            raise NotADirectoryError(f"{path} is not a file!")

        file_type = await PathValidator.get_file_type(file_path)

        if file_type.startswith('text/'):
            return await self.create_output_text(file_path)
        elif file_type.startswith('image/'):
            return await self.create_output_image(file_path, file_type)
        else:
            return await self.create_output_default()

    @staticmethod
    async def create_output_text(file_path: Path) -> list[TextContent]:
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
        return [
            TextContent(
                type="text",
                text=content
            )
        ]

    @staticmethod
    async def create_output_image(file_path: Path, file_type: str) -> list[ImageContent]:
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        return [
            ImageContent(
                type="image",
                data=base64.b64encode(content).decode('utf-8'),
                mimeType=file_type
            )
        ]

    @staticmethod
    async def create_output_default() -> list[TextContent]:
        return [
            TextContent(
                type="text",
                text="Unsupported file type"
            )
        ]
