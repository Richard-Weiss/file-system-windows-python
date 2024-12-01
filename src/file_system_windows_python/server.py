import mcp.server.stdio
from mcp.server import Server
from mcp.types import *
from pydantic import AnyUrl

from file_system_windows_python.handlers.add_note import AddNoteHandler
from file_system_windows_python.tools.util.tool_factory import ToolFactory
from file_system_windows_python.tools.util.tool_registry import ToolRegistry

server = Server("file-system-windows-python")


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
    return [ToolFactory.create_add_note_tool()]


@server.call_tool()
async def handle_call_tool(
        name: str, arguments: dict | None
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    handler = ToolRegistry().get_handler(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    return await handler.execute(arguments)


async def main(args) -> None:
    tool_registry = ToolRegistry()
    tool_registry.register_tool("add-note", ToolFactory.create_add_note_tool(), AddNoteHandler())

    options = server.create_initialization_options()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            options
        )
