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
from file_system_windows_python.tools.tools import Tools
from file_system_windows_python.util.logging import log_execution
from file_system_windows_python.util.path_validator import PathValidator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ReadFileHandler(Handler):
    """
    Handler for reading files.

    This handler reads the contents of a specified file and returns it as a list of TextContent or ImageContent objects.
    """

    @log_execution(Tools.READ_FILE)
    async def execute(self, arguments: dict) -> List[TextContent | ImageContent]:
        """
        Execute the handler to read a file.

        Args:
            arguments (dict): A dictionary of arguments, including:
                - path (str): The path of the file to read.

        Returns:
            List[TextContent | ImageContent]: A list of content objects representing the file contents.

        Raises:
            ValueError: If the path argument is missing.
            Exception: If an error occurs while reading the file.
        """
        path = arguments.get("path")
        if not path:
            raise ValueError("Missing path")

        await PathValidator.validate_file_path(path)
        file_path = await PathValidator.resolve_absolute_path(path)

        try:
            try:
                return await self.create_output_text(file_path)
            except UnicodeDecodeError:
                file_type = await PathValidator.get_file_type(file_path)
                if file_type.startswith('image/'):
                    return await self.create_output_image(file_path, file_type)
                elif file_type == 'application/pdf':
                    return await self.create_output_pdf_as_images(file_path)
                else:
                    return [TextContent(type="text", text=f"File type {file_type} is not allowed!")]
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            return [TextContent(type="text", text=f"Error reading file: {str(e)}")]

    @staticmethod
    async def create_output_text(file_path: Path) -> List[TextContent]:
        """
        Create the output list of TextContent objects for a text file.

        Args:
            file_path (Path): The path of the text file.

        Returns:
            List[TextContent]: A list of TextContent objects representing the file contents.
        """
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
        if not content:
            return [TextContent(type="text", text="File is empty")]
        return [TextContent(type="text", text=f"<fileContent>{content}</fileContent>")]

    @staticmethod
    async def create_output_image(file_path: Path, file_type: str) -> List[ImageContent]:
        """
        Create the output list of ImageContent objects for an image file.

        Args:
            file_path (Path): The path of the image file.
            file_type (str): The MIME type of the image file.

        Returns:
            List[ImageContent]: A list of ImageContent objects representing the file contents.
        """
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        return [ImageContent(
            type="image",
            data=base64.b64encode(content).decode('utf-8'),
            mimeType=file_type
        )]

    @staticmethod
    async def create_output_pdf_as_images(file_path: Path) -> List[Union[ImageContent, TextContent]]:
        """
        Create the output list of ImageContent and TextContent objects for a PDF file.

        Args:
            file_path (Path): The path of the PDF file.

        Returns:
            List[Union[ImageContent, TextContent]]: A list of content objects representing the PDF contents.
        """
        results = []
        text_only = False

        with fitz.open(str(file_path)) as pdf:
            page_count = len(pdf)

            if page_count > 100:
                text_only = True
                results.append(TextContent(
                    type="text",
                    text="PDF contains more than 100 pages, only text is returned."
                ))

            extracted_texts = []
            tasks = []
            for page_num in range(page_count):
                page = pdf[page_num]
                tasks.append(
                    ReadFileHandler.process_page(
                        page,
                        text_only,
                        extracted_texts,
                        results
                    )
                )

            await asyncio.gather(*tasks)

            if text_only:
                results.append(TextContent(
                    type="text",
                    text=f"<extractedText>{''.join(extracted_texts)}</extractedText>"
                ))

        return results

    @staticmethod
    async def process_page(
            page,
            text_only: bool,
            extracted_texts: List[str],
            results: List[Union[ImageContent, TextContent]]):
        """
        Process a single page of a PDF file.

        Args:
            page: The PDF page to process.
            text_only (bool): Whether to extract text only.
            extracted_texts (List[str]): A list to store extracted texts.
            results (List[Union[ImageContent, TextContent]]): A list to store content objects.

        Returns:
            None
        """
        text = page.get_text()

        if text_only:
            extracted_texts.append(text)
        else:
            optimal_zoom = await ReadFileHandler._calculate_zoom(page)
            webp_bytes = await ReadFileHandler._convert_page_to_webp(page, optimal_zoom)

            results.append(ImageContent(
                type="image",
                data=base64.b64encode(webp_bytes).decode('utf-8'),
                mimeType="image/webp"
            ))
            results.append(TextContent(
                type="text",
                text=f"<extractedText>{text}</extractedText>"
            ))

    @staticmethod
    async def _convert_page_to_webp(page, optimal_zoom: float):
        """
        Convert a PDF page to a WebP image.

        Args:
            page: The PDF page to convert.
            optimal_zoom (float): The zoom level for the conversion.

        Returns:
            bytes: The WebP image data.
        """
        def _convert():
            pix = page.get_pixmap(matrix=fitz.Matrix(optimal_zoom, optimal_zoom))
            mode = "RGBA" if pix.alpha else "RGB"
            img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
            output_buffer = io.BytesIO()
            img.save(output_buffer, format="WEBP", quality=80, method=6)
            return output_buffer.getvalue()

        return await asyncio.to_thread(_convert)

    @staticmethod
    async def _calculate_zoom(page) -> float:
        """
        Calculate the optimal zoom level for converting a PDF page to an image.

        Args:
            page: The PDF page to convert.

        Returns:
            float: The optimal zoom level.
        """
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
