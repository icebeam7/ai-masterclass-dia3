"""Pure functions used by the real MCP server; easy to unit-test."""
import json
from app.safety import check_prompt_and_documents

CATEGORIES = ("acceso", "seguridad", "hardware", "software", "otros")

def knowledge_tool(question: str, search=None) -> str:
    if len(question.strip()) < 5 or len(question) > 1500:
        raise ValueError("La consulta debe tener entre 5 y 1500 caracteres")
    check_prompt_and_documents(question)
    if search is None:
        from app.knowledge import search_documents
        search = search_documents
    docs = search(question)
    check_prompt_and_documents(question, [doc["content"] for doc in docs])
    return json.dumps({"results": docs, "count": len(docs)}, ensure_ascii=False)

def categories_tool() -> str:
    return json.dumps({"categories": list(CATEGORIES), "priorities": ["baja", "media", "alta"],
        "requires_human_approval": True, "allowed_actions": ["propose_ticket"],
        "note": "Este servidor MCP NO permite escribir tickets ni acceder a Cosmos DB."}, ensure_ascii=False)
