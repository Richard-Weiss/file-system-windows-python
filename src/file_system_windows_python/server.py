import logging
from typing import Any

import mcp.server.stdio
from mcp import types
from mcp.server import Server
from mcp.types import Resource, Prompt, GetPromptResult, Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl

from file_system_windows_python.tools.util.tool_factory import ToolFactory
from file_system_windows_python.tools.util.tool_registry import ToolRegistry

server = Server("file-system-windows-python")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def initialize_singletons():
    """Initialize core application components"""
    ToolRegistry()


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """
    List available resources.
    """
    raise NotImplementedError()


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific resource by its uri.
    """
    raise NotImplementedError()


@server.list_prompts()
async def handle_list_prompts() -> list[Prompt]:
    """
    List available prompts.
    Each prompt can have optional arguments to customize its behavior.
    """
    raise NotImplementedError()


@server.get_prompt()
async def handle_get_prompt(
        name: str, arguments: dict[str, str] | None
) -> GetPromptResult:
    """
    Generate a prompt by combining arguments with server state.
    """
    raise NotImplementedError()


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [ToolFactory.create_list_allowed_directories_tool(),
            ToolFactory.create_list_denied_directories_tool(),
            ToolFactory.create_ls_tool(),
            ToolFactory.create_read_file_tool()]


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
