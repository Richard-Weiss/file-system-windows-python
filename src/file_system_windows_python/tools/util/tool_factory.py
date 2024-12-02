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
