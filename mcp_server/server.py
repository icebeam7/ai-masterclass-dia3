"""Real MCP SDK 2.x server, local Streamable HTTP transport."""
import os
from mcp.server.mcpserver import MCPServer
from mcp_server.service import knowledge_tool, categories_tool
from mcp_server.telemetry import record_call

mcp = MCPServer("EnterpriseKnowledgeMCP")

@mcp.tool()
def search_knowledge(question: str) -> str:
    """Busca procedimientos y políticas en Azure AI Search; documentos originados en Blob Storage."""
    try:
        result = knowledge_tool(question)
        record_call("search_knowledge", {"query": question[:180]}, "success")
        return result
    except Exception:
        record_call("search_knowledge", {"query": question[:180]}, "error")
        raise

@mcp.tool()
def get_ticket_categories() -> str:
    """Consulta categorías, prioridades y reglas de aprobación; operación de solo lectura."""
    record_call("get_ticket_categories", {}, "success")
    return categories_tool()

if __name__ == "__main__":
    # Solo loopback para la clase. En producción: HTTPS, OAuth, aislamiento, autorización.
    mcp.run(transport="streamable-http", host="127.0.0.1", port=int(os.getenv("MCP_PORT", "8001")), json_response=True, stateless_http=True)
