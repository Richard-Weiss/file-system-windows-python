import logging

import aiofiles
from mcp.types import TextContent

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.schemas.write_file_arguments import WriteFileArguments
from file_system_windows_python.tools.tools import Tools
from file_system_windows_python.util.logging import log_execution
from file_system_windows_python.util.path_validator import PathValidator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class WriteFileHandler(Handler):
    """
    Handler for writing content to a file.

    This handler writes the provided content to the specified file path.
    """

    @log_execution(Tools.WRITE_FILE)
    async def execute(self, arguments: dict) -> list[TextContent]:
        """
        Execute the handler to write content to a file.

        Args:
            arguments (dict): A dictionary of arguments, including:
                - path (str): The path of the file to write to.
                - content (str): The content to write to the file.

        Returns:
            list[TextContent]: A list containing a TextContent object with a success message.

        Raises:
            ValueError: If the path or content argument is missing.
        """
        args = WriteFileArguments(**arguments)
        path = args.path
        content = args.content

        await PathValidator.validate_file_path(path)
        file_path = await PathValidator.resolve_absolute_path(path)

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
