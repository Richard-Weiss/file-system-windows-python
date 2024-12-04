from mcp import types


class ToolFactory:
    @staticmethod
    def create_add_note_tool() -> types.Tool:
        return types.Tool(
            name="add-note",
            description="Add a new note",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["name", "content"],
            },
        )

    @staticmethod
    def create_list_allowed_directories_tool() -> types.Tool:
        return types.Tool(
            name="list-allowed-directories",
            description="List allowed directories",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        )

    @staticmethod
    def create_list_denied_directories_tool() -> types.Tool:
        return types.Tool(
            name="list-denied-directories",
            description="List denied directories",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        )

    @staticmethod
    def create_ls_tool() -> types.Tool:
        return types.Tool(
            name="ls",
            description="List directories using an absolute path. Optionally specify a page number.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "page": {"type": "integer"},
                },
                "required": ["path"],
            },
        )

    @staticmethod
    def create_read_file_tool() -> types.Tool:
        return types.Tool(
            name="read-file",
            description="Reads the contents of a file. Allowed types are text/plain and images.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        )
