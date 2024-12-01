import argparse
import asyncio
import os

from . import server


def validate_args(args):
    if len(args.allow) != len(set(args.allow)):
        raise ValueError("Duplicate paths found in --allow")
    if len(args.deny) != len(set(args.deny)):
        raise ValueError("Duplicate paths found in --deny")

    for path in args.allow + args.deny:
        if not os.path.exists(path):
            raise ValueError(f"Path does not exist: {path}")
        if not os.path.isdir(path):
            raise ValueError(f"Path is not a directory: {path}")


def main():
    """Main entry point for the package."""
    from .util.config import Config

    parser = argparse.ArgumentParser(description='File System MCP Server')
    parser.add_argument(
        '--allow',
        action='append',
        required=True,
        default=[],
        help='Allowed paths (can specify multiple by repeating flag)')
    parser.add_argument(
        '--deny',
        action='append',
        default=[],
        help='Denied paths (can specify multiple by repeating flag)')
    args = parser.parse_args()

    validate_args(args)
    config = Config()
    config.allow = args.allow
    config.deny = args.deny

    asyncio.run(server.main())


__all__ = ['main', 'server']
