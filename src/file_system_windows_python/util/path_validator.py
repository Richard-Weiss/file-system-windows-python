import logging
from pathlib import Path

import aiofiles
from magika import Magika
from pathvalidate import validate_filepath, sanitize_filepath

from file_system_windows_python.util.config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PathValidationError(ValueError):
    """Custom exception for path validation failures"""
    pass


class PathValidator:
    """
    Validate a file path against security checks and allowed/denied paths.

    Args:
        path_str: The path to validate

    Returns:
        None

    Raises:
        PathValidationError: If the path fails any validation check
    """

    @staticmethod
    async def validate_path(path_str: str):
        try:
            logger.debug("Starting path validation")
            logger.debug("Resolving allowed paths")
            allowed_paths = [Path(str(p)).resolve() for p in Config().allow]
            logger.debug("Resolving denied paths")
            denied_paths = [Path(str(p)).resolve() for p in (Config().deny or [])]

            logger.debug("Sanitizing path")
            sanitized = sanitize_filepath(path_str, platform='Windows')
            validate_filepath(sanitized, platform='Windows')

            logger.debug("Resolving absolute path")
            abs_path = Path(sanitized).resolve()

            if not abs_path.exists():
                raise PathValidationError(f"Path {abs_path} does not exist!")

            if not abs_path.is_file():
                raise PathValidationError(f"Path {abs_path} is not a file!")

            if not any(PathValidator._is_subpath(abs_path, allowed) for allowed in allowed_paths):
                raise PathValidationError(f"Path {abs_path} is not within allowed paths!")

            if denied_paths:
                for denied in denied_paths:
                    if PathValidator._is_subpath(abs_path, denied):
                        raise PathValidationError(f"Path {abs_path} is within denied path {denied}!")

            logger.debug("Checking file type")
            magika = Magika()
            async with aiofiles.open(str(abs_path), 'rb') as f:
                content = await f.read()
                result = magika.identify_bytes(content)
                if result.output.mime_type != 'text/plain':
                    raise PathValidationError(f"File type {result.output.mime_type} is not allowed!")

            logger.debug("Path validation successful!")
        except Exception as e:
            if isinstance(e, PathValidationError):
                raise
            raise PathValidationError(f"Path validation failed: {str(e)}")

    @staticmethod
    def _is_subpath(path: Path, parent: Path) -> bool:
        """
        Check if a path is a subpath of another path.

        Args:
            path: The path to check
            parent: The potential parent path

        Returns:
            bool: True if path is a subpath of parent
        """
        try:
            path = Path(str(path)).resolve()
            parent = Path(str(parent)).resolve()

            return str(path).startswith(str(parent))
        except (ValueError, RuntimeError) as e:
            raise PathValidationError(f"Failed to resolve path during comparison: {str(e)}")
