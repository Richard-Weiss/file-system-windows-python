import logging
from functools import wraps

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def log_execution(tool_name):
    """
    Decorator to log the execution of a function.

    Args:
        tool_name (str): Tool name to include in the log.

    Returns:
        function: The decorated function with logging.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            """
            Wrapper function to log before and after the execution of the decorated function.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                Any: The result of the decorated function.
            """
            logger.debug(f"Executing {tool_name} handler")
            result = await func(*args, **kwargs)
            logger.debug(f"Finished executing {tool_name} handler")
            return result
        return wrapper
    return decorator

