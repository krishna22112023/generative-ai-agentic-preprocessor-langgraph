from mcp.server.fastmcp import FastMCP


import sys
import pyprojroot
root = pyprojroot.find_root(pyprojroot.has_dir("config"))
sys.path.append(str(root))

from src.utils import read,create,delete

mcp = FastMCP("MinIO")

@mcp.tool()
def list_objects(prefix: str) -> list:
    """
    List objects in the bucket. Use the prefix to emulate folder listing.
    """
    return str(read.list_object(prefix))

@mcp.tool()
def download_objects(prefix: str) -> bool:
    """
    Download all objects under a given prefix (simulating a folder)
    and preserve the folder structure locally.
    """
    return read.download_object(prefix)

@mcp.tool()
def upload_objects(file_path: str, prefix: str) -> bool:
    """
    Upload a single file or directory of files to the bucket at the given prefix.
    """
    return create.upload_object(file_path,prefix)

@mcp.tool()
def delete_objects(prefix: str) -> bool:
    """
    Delete all objects under a given prefix (simulating a folder).
    """
    return delete.delete_object(prefix)

if __name__ == "__main__":
    mcp.run(transport="stdio")