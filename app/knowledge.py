"""Reutiliza Search y embeddings REALES de la Clase 2."""
from rag_clase2.app.config import Settings as RagSettings
from rag_clase2.app.foundry import FoundryService
from rag_clase2.app.search import KnowledgeSearch

def search_documents(query: str, top: int = 4):
    if not query or len(query)>1500: raise ValueError('Consulta vacía o demasiado larga')
    settings=RagSettings.from_env()
    foundry=FoundryService(settings)
    vector=foundry.embed([query])[0]
    retrieved=KnowledgeSearch(settings).retrieve(query, vector, mode='hybrid', top=min(top,settings.top_k))
    # Devolver resultados breves y con origen explícito
    return [{'source':r['source'], 'content':r['content'][:1600], 'score':r['score']} for r in retrieved]
