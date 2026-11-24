"""Prueba de extremo a extremo, usa tokens y recursos reales."""
from rag_clase2.app.config import Settings
from rag_clase2.app.foundry import FoundryService
from rag_clase2.app.search import KnowledgeSearch

def main():
    cfg=Settings.from_env()
    foundry=FoundryService(cfg)
    search=KnowledgeSearch(cfg)
    print('Comprobando modelo y embeddings en Foundry...')
    assert foundry.embed(['prueba de conexión'])[0]
    result=foundry.answer('Responde solamente: OK',None,grounded=False)
    print('Modelo:',result['answer'][:120])
    print('Comprobando servicio e índice Azure AI Search...')
    print('Documentos en índice:',search.count())
    print('Conexiones OK (esta prueba no garantiza calidad de RAG).')

if __name__=='__main__': main()
