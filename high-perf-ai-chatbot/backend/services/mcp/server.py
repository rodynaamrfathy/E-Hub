from mcp.server.fastmcp import FastMCP
from . import tools

mcp = FastMCP("postgres-mcp")

# Register tools
mcp.add_tool(tools.query_db)
mcp.add_tool(tools.execute_db)

if __name__ == "__main__":
    mcp.run()
