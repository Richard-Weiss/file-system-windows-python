import asyncio
import base64
import io
import logging
from pathlib import Path
from typing import List, Union

import aiofiles
import fitz
from PIL import Image
from mcp.types import TextContent, ImageContent

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.util.path_validator import PathValidator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ReadFileHandler(Handler):
    async def execute(self, arguments: dict | None) -> List[TextContent | ImageContent]:
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
    async def create_output_image(file_path: Path, file_type: str) -> List[ImageContent]:
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
    async def create_output_pdf_as_images(file_path: Path) -> List[Union[ImageContent, TextContent]]:
        results = []
        text_only = False
        with fitz.open(str(file_path)) as pdf:
            if len(pdf) > 100:
                text_only = True
                results.append(TextContent(
                    type="text",
                    text="PDF contains more than 100 pages, only text is returned.")
                )

            extracted_texts = []
            for page_num in range(len(pdf)):
                page = pdf[page_num]
                text = ReadFileHandler._extract_page_text(page, page_num)

                if text_only:
                    extracted_texts.append(text)
                else:
                    optimal_zoom = ReadFileHandler.calculate_zoom(page)
                    pix = page.get_pixmap(matrix=fitz.Matrix(optimal_zoom, optimal_zoom))
                    img_bytes = pix.tobytes("png")
                    buffer = io.BytesIO(img_bytes)
                    img = Image.open(buffer)
                    webp_buffer = io.BytesIO()
                    img.save(webp_buffer, format="WEBP", quality=80, method=6)
                    webp_bytes = webp_buffer.getvalue()
                    results.append(ImageContent(
                        type="image",
                        data=base64.b64encode(webp_bytes).decode('utf-8'),
                        mimeType="image/webp"
                    ))
                    results.append(TextContent(
                        type="text",
                        text=f"<extractedText>{text}</extractedText>"
                    ))

            if text_only:
                results.append(TextContent(
                    type="text",
                    text=f"<extractedText>{''.join(extracted_texts)}</extractedText>"
                ))
        logger.debug("Done processing PDF")
        logger.debug(f"Results length: {len(results)}")
        return results

    @staticmethod
    def _extract_page_text(page, page_num):
        logger.debug(f"Extracting text from page {page_num + 1}")
        text = page.get_text()
        logger.debug(f"Extracted text from page {page_num + 1}: {text}")
        return text

    @staticmethod
    def calculate_zoom(page):
        rect = page.rect
        orig_width = rect.width
        orig_height = rect.height

        low = 1
        high = 10
        limit = 2 ** 10 + 2 ** 7

        while low < high:
            mid = (low + high) / 2
            new_width = orig_width * mid
            new_height = orig_height * mid

            if new_width >= limit or new_height >= limit:
                high = mid
            else:
                low = mid + 0.1

        return low
