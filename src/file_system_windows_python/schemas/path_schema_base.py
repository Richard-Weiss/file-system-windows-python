from pydantic import BaseModel, Field


class PathSchemaBase(BaseModel):
    """
    Base schema for path-related operations.

    Attributes:
        path (str): The path to be validated or processed.
    """
    path: str = Field(min_length=1)
