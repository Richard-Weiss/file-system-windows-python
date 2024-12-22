from dataclasses import dataclass
from typing import Type

from mcp.types import Tool

from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.handlers.list_allowed_directories import ListAllowedDirectoriesHandler
from file_system_windows_python.handlers.list_denied_directories import ListDeniedDirectoriesHandler
from file_system_windows_python.handlers.ls import LsHandler
from file_system_windows_python.handlers.read_file import ReadFileHandler
from file_system_windows_python.handlers.write_file import WriteFileHandler
from file_system_windows_python.tools.tools import Tools


@dataclass
class ToolDefinition:
    """Combines tool metadata with its handler implementation"""
    name: str
    description: str
    inputSchema: dict
    handler_class: Type[Handler]


class ToolRegistry:
    _instance = None
    _tools: dict[str, ToolDefinition] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ToolRegistry, cls).__new__(cls, *args, **kwargs)
            cls._instance.__register_default_tools()
        return cls._instance

    def get_tool(self, name: str) -> Tool | None:
        """Get Tool metadata for MCP interface"""
        if tool_def := self._tools.get(name):
            return Tool(
                name=tool_def.name,
                description=tool_def.description,
                inputSchema=tool_def.inputSchema
            )
        return None

    def get_handler(self, name: str) -> Handler | None:
        """Get Handler instance for tool execution"""
        if tool_def := self._tools.get(name):
            return tool_def.handler_class()
        return None

    def list_tools(self) -> list[Tool]:
        """Get all registered tools"""
        return [self.get_tool(name) for name in self._tools]

    def register_tool(self, tool_def: ToolDefinition):
        """Register a tool definition"""
        self._tools[tool_def.name] = tool_def

    def __register_default_tools(self):
        """Register all default tools and their handlers."""
        self.register_tool(
            ToolDefinition(
                name=Tools.LIST_ALLOWED_DIRECTORIES,
                description="List allowed directories",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
                handler_class=ListAllowedDirectoriesHandler
            ))
        self.register_tool(
            ToolDefinition(
                name=Tools.LIST_DENIED_DIRECTORIES,
                description="List denied directories",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
                handler_class=ListDeniedDirectoriesHandler
            ))
        self.register_tool(
            ToolDefinition(
                name=Tools.LS,
                description="List directories using an absolute path. Optionally specify a page number.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "page": {"type": "integer"},
                    },
                    "required": ["path"],
                },
                handler_class=LsHandler
            ))
        self.register_tool(
            ToolDefinition(
                name=Tools.READ_FILE,
                description="Reads the contents of a file. Allowed types are text/plain and images.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                    },
                    "required": ["path"],
                },
                handler_class=ReadFileHandler
            ))
        self.register_tool(
            ToolDefinition(
                name=Tools.WRITE_FILE,
                description="Writes content to a file at the specified absolute path. Since the content is replaced, make sure to call read-file first and include everything without placeholders. Do not end the content with an emoji.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["path", "content"],
                },
                handler_class=WriteFileHandler
            ))
