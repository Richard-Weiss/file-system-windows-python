# file-system-windows-python MCP server

A Model Context Protocol (MCP) server that provides secure access to the Windows file system with image and PDF read support.

**This MCP server is *as is* and published mainly for illustration purposes. Do not expect support.**

## Components

### Tools

The server implements the following tools:

- `list-allowed-directories`: Lists directories that have been allowed for access
- `list-denied-directories`: Lists directories that have been denied access
- `ls`: Lists contents of a directory
  - Takes "path" as required string argument
  - Optional "page" argument for pagination (50 items per page)
- `read-file`: Reads the contents of files
  - Takes "path" as required string argument
  - Supports text files, PDFs (converted to images with text extraction), and images
  - Returns content wrapped in `<fileContent>` tags for text files
- `write-file`: Writes content to a file
  - Takes "path" and "content" as required string arguments
  - Updates the file content and returns success message

## Configuration

The server requires configuration of allowed and denied directories for security:

```bash
file-system-windows-python --allow /path/to/allowed/dir [--deny /path/to/denied/dir]
```

Example:
```bash
file-system-windows-python --allow "G:/Claude" --deny "G:/Claude/not for you"
```

Multiple arguments can be chained like this:
```bash
file-system-windows-python --allow "G:/Claude" --allow "C:/Users/dev/Developer_Tools/PycharmProjects" --deny "G:/Claude/not for you"
```

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

Example configuration:
  ```bash
  "mcpServers": 
    "file-system-windows-python": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/dev/Developer_Tools/PycharmProjects/file-system-windows-python", // replace with own path
        "run",
        "file-system-windows-python",
        "--allow",
        "G:/Claude" //replace with own path
      ]
    }
  ```
