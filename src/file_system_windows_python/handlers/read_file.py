import asyncio
import base64
import logging
from pathlib import Path
from typing import List

import aiofiles
import fitz
from mcp.types import TextContent, ImageContent

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.util.path_validator import PathValidator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ReadFileHandler(Handler):
    async def execute(self, arguments: dict | None) -> list[TextContent | ImageContent]:
        logger.debug("Executing read file handler")

        if not arguments or "path" not in arguments:
            raise ValueError("Missing required 'path' argument")

        path = arguments["path"]
        await PathValidator.validate_file_path(path)
        file_path = Path(path).resolve()

        try:
            async with asyncio.timeout(10):
                try:
                    return await self.create_output_text(file_path)
                except UnicodeDecodeError:
                    file_type = await PathValidator.get_file_type(file_path)
                    if file_type.startswith('image/'):
                        return await self.create_output_image(file_path, file_type)
                    elif file_type == 'application/pdf':
                        return await self.create_output_pdf_as_images(file_path)
                    else:
                        return [TextContent(
                            type="text",
                            text=f"File type {file_type} is not allowed!"
                        )]

        except asyncio.TimeoutError:
            return [TextContent(
                type="text",
                text="File read operation timed out"
            )]
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            return [TextContent(
                type="text",
                text=f"Error reading file: {str(e)}"
            )]

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

    @staticmethod
    async def create_output_pdf_as_images(file_path: Path, max_pages: int = 10) -> List[ImageContent]:
        pdf = fitz.open(str(file_path))
        results = []

        for page_num in range(min(len(pdf), max_pages)):
            page = pdf[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("png")

            results.append(ImageContent(
                type="image",
                data=base64.b64encode(img_bytes).decode('utf-8'),
                mimeType="image/png"
            ))

        pdf.close()
        return results
