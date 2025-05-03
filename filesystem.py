from mcp import types
from mcp.server.fastmcp import FastMCP
from pathlib import Path

cwd = Path.home() / 'Desktop'

mcp = FastMCP("filesystem")

@mcp.tool()
async def get_cwd() -> types.TextContent:
    """Get the current working directory."""
    return types.TextContent(type='text', text=str(cwd))

@mcp.tool()
async def list_cwd() -> types.TextContent:
    """Get the files from the current working directory."""
    return types.TextContent(type='text', text=str(list(cwd.glob('*'))))

@mcp.tool()
async def search_for_file(file_name: str) -> types.TextContent:
    """Search recursively for a file starting from the current working directory
    given the exact name of the file.
    The file format of the file must be provided.
    """
    return types.TextContent(type='text', text=str(list(cwd.rglob(f'*{file_name}'))))

@mcp.tool()
async def search_for_file_partial(file_or_folder_name: str) -> types.TextContent:
    """Search recursively for a file or folder starting from the current working directory."""
    return types.TextContent(type='text', text=str(list(cwd.rglob(f'*{file_or_folder_name}*'))))

@mcp.tool()
async def make_desktop_cwd() -> types.TextContent:
    """Make the Desktop the current working directory."""
    global cwd
    cwd = Path.home() / 'Desktop'
    return types.TextContent(type='text', text='Done')

@mcp.tool()
async def make_folder_cwd(folder_name: str) -> types.TextContent:
    """Make a folder the current working directory.
    That folder must be present in the previous cwd.
    """
    global cwd
    new_cwd = cwd / folder_name
    if new_cwd.exists():
        result = 'Done'
        cwd = new_cwd
    else:
        result = f'Folder not found. The previous cwd is maintained: {cwd}'
    return types.TextContent(type='text', text=result)

if __name__ == '__main__':
    mcp.run(transport='stdio') 