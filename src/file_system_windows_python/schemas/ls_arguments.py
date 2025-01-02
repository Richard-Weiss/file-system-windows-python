from pydantic import Field

from file_system_windows_python.schemas.path_schema_base import PathSchemaBase


class LsArguments(PathSchemaBase):
    """
    Arguments for the 'ls' command.

    Attributes:
        page (int): The page number for pagination, default is 1.
    """
    page: int = Field(default=1, ge=1)
