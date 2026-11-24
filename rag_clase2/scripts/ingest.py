"""Ingesta real: leer Azure Blob Storage -> fragmentar -> Foundry -> AI Search."""
import argparse
from rag_clase2.app.config import Settings
from rag_clase2.app.blob_documents import load_blob_chunks
from rag_clase2.app.foundry import FoundryService
from rag_clase2.app.search import KnowledgeSearch

def run():
    parser=argparse.ArgumentParser(description='Carga documentos ficticios en Azure AI Search')
    parser.add_argument('--batch-size',type=int,default=12)
    args=parser.parse_args()
    if not 1 <= args.batch_size <= 50: parser.error('--batch-size debe estar entre 1 y 50')
    cfg=Settings.from_env()
    model=FoundryService(cfg)
    index=KnowledgeSearch(cfg)
    chunks=load_blob_chunks(cfg)
    print(f'1/3 Azure Blob Storage: {len(chunks)} fragmentos leídos de archivos .md')
    state=index.ensure_index()
    print(f'2/3 Azure AI Search: índice {cfg.search_index} ({state})')
    docs=[]
    for i in range(0,len(chunks),args.batch_size):
        batch=chunks[i:i+args.batch_size]
        vectors=model.embed([c.content for c in batch])
        docs.extend({'id':c.id,'title':c.title,'source':c.source,
                     'content':c.content,'content_vector':vec} for c,vec in zip(batch,vectors))
        print(f'Embeddings generados: {len(docs)}/{len(chunks)}')
    print(f'3/3 Documentos cargados: {index.upload(docs)}')
    print('Nota: Azure AI Search puede tardar unos segundos en reflejar todos los registros.')

if __name__=='__main__': run()
