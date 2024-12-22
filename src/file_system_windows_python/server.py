import logging
from typing import Any

import mcp.server.stdio
from mcp import types
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from file_system_windows_python.tools.util.tool_registry import ToolRegistry

server = Server("file-system-windows-python")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def initialize_singletons():
    """Initialize core application components"""
    ToolRegistry()


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return ToolRegistry().list_tools()


@server.call_tool()
async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    logger.debug(f"Calling tool: {name}")
    handler = ToolRegistry().get_handler(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")

    result = await handler.execute(arguments)

    if isinstance(result[0], types.TextContent):
        logger.debug(f"Result for tool {name} with arguments {arguments}: '{result[0].text}'")

    return result


async def main() -> None:
    await initialize_singletons()
    options = server.create_initialization_options()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            options
        )
