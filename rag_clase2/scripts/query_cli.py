"""Consulta alternativa sin abrir Streamlit."""
import argparse
from rag_clase2.app.config import Settings
from rag_clase2.app.foundry import FoundryService
from rag_clase2.app.search import KnowledgeSearch

p=argparse.ArgumentParser()
p.add_argument('question')
p.add_argument('--mode',choices=('keyword','hybrid'),default='hybrid')
a=p.parse_args()
cfg=Settings.from_env(); llm=FoundryService(cfg); index=KnowledgeSearch(cfg)
vector=llm.embed([a.question])[0] if a.mode=='hybrid' else None
chunks=index.retrieve(a.question,vector,a.mode,cfg.top_k)
for i,c in enumerate(chunks,1): print(f"[F{i}] {c['source']}: {c['content'][:180]}...")
print('\nRESPUESTA:',llm.answer(a.question,chunks)['answer'])
