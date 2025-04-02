from langchain_mcp_adapters.client import MultiServerMCPClient

import sys
import pyprojroot
root = pyprojroot.find_root(pyprojroot.has_dir("config"))
sys.path.append(str(root))

async def get_client():
    """
    This is the async version of the tool_node with MCP
    """

    mcp_client = MultiServerMCPClient(
        {   
        "minIO": {
            "command": "python",
            "args": [f"{root}/src/services/mcp/minIO_server.py"],
            "transport": "stdio",
            }
        }
    )
    async with mcp_client:
        mcp_tools = mcp_client.get_tools()
        return mcp_tools