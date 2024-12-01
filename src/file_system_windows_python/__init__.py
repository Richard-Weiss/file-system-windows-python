import argparse
import asyncio

from . import server


def main():
    """Main entry point for the package."""
    from .util.config import Config

    parser = argparse.ArgumentParser(description='File System MCP Server')
    parser.add_argument(
        '--allow',
        action='append',
        default=[],
        help='Allowed paths (can specify multiple by repeating flag)')
    parser.add_argument(
        '--deny',
        action='append',
        default=[],
        help='Denied paths (can specify multiple by repeating flag)')
    args = parser.parse_args()

    config = Config()
    config.allow = args.allow
    config.deny = args.deny

    asyncio.run(server.main(args))


__all__ = ['main', 'server']
