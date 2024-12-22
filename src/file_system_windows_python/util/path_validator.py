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
    async def validate_file_path(path_str: str):
        await PathValidator._validate_path(path_str, is_file=True)

    @staticmethod
    async def validate_directory_path(path_str: str):
        await PathValidator._validate_path(path_str, is_file=False)

    @staticmethod
    async def _validate_path(path_str: str, is_file: bool):
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

            if is_file and not abs_path.is_file():
                raise PathValidationError(f"Path {abs_path} is not a file!")
            elif not is_file and not abs_path.is_dir():
                raise PathValidationError(f"Path {abs_path} is not a directory!")

            if not any(PathValidator._is_subpath(abs_path, allowed) for allowed in allowed_paths):
                raise PathValidationError(f"Path {abs_path} is not within allowed paths!")

            if denied_paths:
                for denied in denied_paths:
                    if PathValidator._is_subpath(abs_path, denied):
                        raise PathValidationError(f"Path {abs_path} is within denied path {denied}!")

            if is_file:
                file_type = await PathValidator.get_file_type(abs_path)
                if not file_type.startswith('text/') and not file_type.startswith('image/'):
                    raise PathValidationError(f"File type {file_type} is not allowed!")

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

    @staticmethod
    async def get_file_type(path: Path) -> str:
        try:
            async with aiofiles.open(str(path), 'r', encoding='utf-8') as f:
                await f.read(1024)
                return 'text/plain'
        except UnicodeDecodeError:
            magika = Magika()
            async with aiofiles.open(str(path), 'rb') as f:
                content = await f.read()
                result = magika.identify_bytes(content)
            return result.output.mime_type
