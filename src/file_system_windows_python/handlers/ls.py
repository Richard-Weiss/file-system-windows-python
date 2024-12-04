import logging
from pathlib import Path

from mcp.types import TextContent

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.util.path_validator import PathValidator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class LsHandler(Handler):
    async def execute(self, arguments: dict | None) -> list[TextContent]:

        logger.debug("Executing ls handler")
        path = arguments.get("path")
        if not path:
            raise ValueError("Missing path")
        await PathValidator.validate_directory_path(path)

        page = arguments.get("page", 1)

        dir_path = Path(path).resolve()

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
    async def create_output(items, total_items, page) -> list[TextContent]:
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
