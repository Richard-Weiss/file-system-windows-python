import logging
from pathlib import Path
from typing import List

from mcp.types import TextContent

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.tools.tools import Tools
from file_system_windows_python.util.logging import log_execution
from file_system_windows_python.util.path_validator import PathValidator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class LsHandler(Handler):
    """
    Handler for listing directory contents.

    This handler retrieves the contents of a specified directory and returns it
    as a list of TextContent objects, with pagination support.
    """

    @log_execution(Tools.LS)
    async def execute(self, arguments: dict) -> List[TextContent]:
        """
        Execute the handler to list directory contents.

        Args:
            arguments dict: A dictionary of arguments, including:
                - path (str): The path of the directory to list.
                - page (int, optional): The page number for pagination. Defaults to 1.

        Returns:
            List[TextContent]: A list of TextContent objects representing the directory contents.

        Raises:
            ValueError: If the path argument is missing.
            FileNotFoundError: If the specified directory does not exist.
            NotADirectoryError: If the specified path is not a directory.
        """
        path = arguments.get("path")
        if not path:
            raise ValueError("Missing path")
        await PathValidator.validate_directory_path(path)

        page = arguments.get("page", 1)

        dir_path = Path(path).resolve(strict=True)

        if not dir_path.exists():
            raise FileNotFoundError(f"Directory {path} does not exist")
        if not dir_path.is_dir():
            raise NotADirectoryError(f"{path} is not a directory")

        items = []
        for item in dir_path.iterdir():
            items.append({
                'name': item.name,
                'is_dir': item.is_dir(),
            })

        items.sort(key=lambda _item: (not _item['is_dir'], _item['name'].lower()))

        total_items = len(items)
        start_idx = (page - 1) * 50
        end_idx = start_idx + 50

        page_items = items[start_idx:end_idx]

        text_content_list = await LsHandler.create_output(page_items, total_items, page)

        return text_content_list

    @staticmethod
    async def create_output(
            items: List[dict],
            total_items: int,
            page: int) -> List[TextContent]:
        """
        Create the output list of TextContent objects.

        Args:
            items (List[dict]): The list of directory items for the current page.
            total_items (int): The total number of items in the directory.
            page (int): The current page number.

        Returns:
            List[TextContent]: A list of TextContent objects representing the directory contents.
        """
        total_pages = (total_items + 50 - 1) // 50

        text_content_list = [TextContent(
            type="text",
            text=f"Total items: {total_items} (Page {page} of {total_pages})",
        )]

        for item in items:
            name = item['name'] + ('/' if item['is_dir'] else '')
            text_content_list.append(
                TextContent(
                    type="text",
                    text=name,
                )
            )

        return text_content_list
