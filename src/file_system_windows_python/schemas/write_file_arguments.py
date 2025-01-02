from pydantic import BaseModel, Field

from file_system_windows_python.schemas.path_schema_base import PathSchemaBase


class WriteFileArguments(PathSchemaBase):
    """
    Arguments for writing to a file.

    Attributes:
        content (str): The content to be written to the file.
    """
    content: str = Field(min_length=1)
