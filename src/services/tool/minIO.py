
from langchain_core.tools import tool

import sys
import pyprojroot
root = pyprojroot.find_root(pyprojroot.has_dir("config"))
sys.path.append(str(root))

from src.utils import read,create,delete


@tool()
def list_objects(prefix: str) -> list:
    """
    List objects in the bucket. Use the prefix to emulate folder listing.
    """
    return str(read.list_object(prefix))

@tool()
def download_objects(prefix: str) -> bool:
    """
    Download all objects under a given prefix and preserve the folder structure locally.
    """
    return read.download_object(prefix)

@tool()
def upload_objects(file_path: str, prefix: str) -> bool:
    """
    Upload a single file or directory of files to the bucket at the given prefix.
    """
    return create.upload_object(file_path,prefix)

@tool()
def delete_objects(prefix: str) -> bool:
    """
    Delete all objects under a given prefix (simulating a folder).
    """
    return delete.delete_object(prefix)

tools = [
    list_objects,
    download_objects,
    upload_objects,
    delete_objects
]

