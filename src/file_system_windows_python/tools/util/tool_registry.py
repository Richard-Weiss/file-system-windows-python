from mcp.types import Tool

from file_system_windows_python.handlers.add_note import AddNoteHandler
from file_system_windows_python.handlers.handler import Handler
from file_system_windows_python.handlers.list_allowed_directories import ListAllowedDirectoriesHandler
from file_system_windows_python.handlers.list_denied_directories import ListDeniedDirectoriesHandler
from file_system_windows_python.handlers.ls import LsHandler
from file_system_windows_python.tools.util.tool_factory import ToolFactory


class ToolRegistry:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ToolRegistry, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._tools = {}
            self._handlers = {}
            self._register_default_tools()
            self._initialized = True

    def register_tool(self, name: str, tool: Tool, handler: Handler):
        self._tools[name] = tool
        self._handlers[name] = handler

    def get_tool(self, name: str):
        return self._tools.get(name)

    def get_handler(self, name: str):
        return self._handlers.get(name)

    def _register_default_tools(self):
        """Register all default tools and their handlers."""
        self.register_tool(
            "add-note",
            ToolFactory.create_add_note_tool(),
            AddNoteHandler())
        self.register_tool(
            "list-allowed-directories",
            ToolFactory.create_list_allowed_directories_tool(),
            ListAllowedDirectoriesHandler())
        self.register_tool(
            "list-denied-directories",
            ToolFactory.create_list_denied_directories_tool(),
            ListDeniedDirectoriesHandler())
        self.register_tool(
            'ls',
            ToolFactory.create_ls_tool(),
            LsHandler()
        )
