import asyncio
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
    async def validate_file_path(path_str: str) -> None:
        """
        Validate a file path.

        Args:
            path_str (str): The path to validate.

        Returns:
            None

        Raises:
            PathValidationError: If the path fails any validation check.
        """
        await PathValidator._validate_path(path_str, is_file=True)

    @staticmethod
    async def validate_directory_path(path_str: str) -> None:
        """
        Validate a directory path.

        Args:
            path_str (str): The path to validate.

        Returns:
            None

        Raises:
            PathValidationError: If the path fails any validation check.
        """
        await PathValidator._validate_path(path_str, is_file=False)

    @staticmethod
    async def _validate_path(path_str: str, is_file: bool) -> None:
        """
        Validate a path against security checks and allowed/denied paths.

        Args:
            path_str (str): The path to validate.
            is_file (bool): Whether the path is a file.

        Returns:
            None

        Raises:
            PathValidationError: If the path fails any validation check.
        """
        try:
            logger.debug("Starting path validation")
            logger.debug("Resolving allowed paths")
            allowed_paths = [Path(str(p)).resolve(strict=True) for p in Config().allow]
            logger.debug("Resolving denied paths")
            denied_paths = [Path(str(p)).resolve(strict=True) for p in (Config().deny or [])]

            logger.debug("Resolving absolute path")
            abs_path = await PathValidator.resolve_absolute_path(path_str)

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
                logger.debug("Checking file type")
                file_type = await PathValidator.get_file_type(abs_path)
                logger.debug(f"Pure file type: {file_type}")
                allowed_file_types = (file_type.startswith(('text/', 'image/'))
                                      or file_type == 'application/pdf')
                if not allowed_file_types:
                    raise PathValidationError(f"File type {file_type} is not allowed!")

            logger.debug("Path validation successful!")
        except Exception as e:
            if isinstance(e, PathValidationError):
                raise
            raise PathValidationError(f"Path validation failed: {str(e)}")

    @staticmethod
    async def resolve_absolute_path(path_str: str) -> Path:
        """
        Resolve and create an absolute path, including symlinks.

        Args:
            path_str: The path to resolve

        Returns:
            Path: The resolved absolute path

        Raises:
            PathValidationError: If the path does not exist
        """
        try:
            logger.debug("Sanitizing path")
            sanitized = sanitize_filepath(path_str, platform='Windows')
            validate_filepath(sanitized, platform='Windows')

            logger.debug("Resolving absolute path")
            abs_path = Path(sanitized).resolve(strict=False)

            if abs_path.is_symlink():
                abs_path = abs_path.readlink().resolve(strict=True)
            else:
                abs_path = abs_path.resolve(strict=True)

            if not abs_path.exists():
                raise PathValidationError(f"Path {abs_path} does not exist!")

            return abs_path
        except Exception as e:
            raise PathValidationError(f"Failed to resolve absolute path: {str(e)}")

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
            if path.is_symlink():
                path = path.readlink()
            if parent.is_symlink():
                parent = parent.readlink()

            path = Path(str(path)).resolve(strict=True)
            parent = Path(str(parent)).resolve(strict=True)

            return str(path).startswith(str(parent))
        except (ValueError, RuntimeError) as e:
            raise PathValidationError(f"Failed to resolve path during comparison: {str(e)}")

    @staticmethod
    async def get_file_type(path: Path) -> str:
        """
        Determine the MIME type of the file.

        Args:
            path (Path): The path to the file.

        Returns:
            str: The MIME type of the file.

        Raises:
            PathValidationError: If the file contains null bytes or if there is an error during path validation.
        """
        magika = Magika()
        async with asyncio.timeout(10):
            async with aiofiles.open(str(path), 'rb') as f:
                content = await f.read()
                result = magika.identify_bytes(content)
                mime_type = result.output.mime_type

        if mime_type != 'application/pdf' and not mime_type.startswith('image/'):
            try:
                async with asyncio.timeout(10):
                    async with aiofiles.open(str(path), 'r', encoding='utf-8') as f:
                        content = await f.read()
                        if '\x00' in content:
                            raise PathValidationError(
                                "File contains null bytes! Null bytes aren't currently supported.")
                        return 'text/plain'
            except UnicodeDecodeError:
                pass

        return mime_type
