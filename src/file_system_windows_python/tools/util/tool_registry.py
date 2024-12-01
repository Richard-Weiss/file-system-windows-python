from mcp.types import Tool
from file_system_windows_python.handlers.handler import Handler


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
            self._initialized = True

    def register_tool(self, name: str, tool: Tool, handler: Handler):
        self._tools[name] = tool
        self._handlers[name] = handler

    def get_tool(self, name: str):
        return self._tools.get(name)

    def get_handler(self, name: str):
        return self._handlers.get(name)
