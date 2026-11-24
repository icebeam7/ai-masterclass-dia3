from dotenv import load_dotenv
load_dotenv()
from app.settings import Settings
from app.knowledge import search_documents
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
import requests

cfg=Settings.read()
print('Foundry project:',cfg.endpoint)
print('RAG documents:',len(search_documents('procedimiento para reportar incidente')))
client=CosmosClient(cfg.cosmos_endpoint,credential=DefaultAzureCredential())
container=client.get_database_client(cfg.cosmos_database).get_container_client(cfg.cosmos_container)
print('Cosmos container:',container.read()['id'])
response=requests.get(cfg.api_url+'/health',timeout=5)
response.raise_for_status()
print('Local Ticket API:',response.json())
print('Conexiones comprobadas; la primera llamada al agente se realiza desde la interfaz.')
