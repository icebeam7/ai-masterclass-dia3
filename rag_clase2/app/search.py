"""Índice explícito y búsqueda keyword/híbrida sobre Azure AI Search."""
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchField, SearchFieldDataType,
    VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration,
)
from azure.search.documents.models import VectorizedQuery

class KnowledgeSearch:
    def __init__(self, settings):
        self.settings=settings
        credential=AzureKeyCredential(settings.search_admin_key)
        self.index_client=SearchIndexClient(settings.search_endpoint, credential)
        self.client=SearchClient(settings.search_endpoint,settings.search_index,credential)

    def ensure_index(self):
        d=self.settings.embedding_dimensions
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String,key=True,filterable=True),
            SearchableField(name="title",type=SearchFieldDataType.String),
            SearchableField(name="content",type=SearchFieldDataType.String),
            SimpleField(name="source",type=SearchFieldDataType.String,filterable=True,facetable=True),
            SearchField(name="content_vector",type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True,vector_search_dimensions=d,vector_search_profile_name="vector-profile"),
        ]
        index=SearchIndex(name=self.settings.search_index,fields=fields,
                          vector_search=VectorSearch(
                              algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
                              profiles=[VectorSearchProfile(name="vector-profile",algorithm_configuration_name="hnsw")]))
        try:
            existing=self.index_client.get_index(self.settings.search_index)
            vf=next(f for f in existing.fields if f.name=='content_vector')
            if vf.vector_search_dimensions != d:
                raise ValueError('El índice existente tiene dimensión de embeddings distinta. Cambia AZURE_SEARCH_INDEX.')
            return 'existing'
        except Exception as error:
            from azure.core.exceptions import ResourceNotFoundError
            if not isinstance(error,ResourceNotFoundError):
                raise
        self.index_client.create_index(index)
        return 'created'

    def upload(self, documents: list[dict]):
        if not documents: return 0
        # Subir en lotes pequeños para respetar límites y facilitar diagnóstico.
        for start in range(0,len(documents),100):
            batch=documents[start:start+100]
            results=self.client.upload_documents(documents=batch)
            errors=[result.key for result in results if not result.succeeded]
            if errors: raise RuntimeError(f"Falló la carga de documentos: {errors}")
        return len(documents)

    def retrieve(self,question: str, vector: list[float] | None, mode: str='hybrid', top: int=4) -> list[dict]:
        kwargs={"search_text":question,"select":["id","source","title","content"],"top":top}
        if mode=='hybrid':
            if vector is None: raise ValueError('Se requiere vector de consulta para modo híbrido')
            kwargs['vector_queries']=[VectorizedQuery(vector=vector,k_nearest_neighbors=top,fields='content_vector')]
        elif mode != 'keyword':
            raise ValueError('mode debe ser hybrid o keyword')
        results=self.client.search(**kwargs)
        return [{"id":x['id'],"source":x['source'],"title":x['title'],
                 "content":x['content'],"score":x.get('@search.score')} for x in results]

    def count(self):
        return self.client.get_document_count()
