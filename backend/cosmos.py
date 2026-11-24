"""Persistencia REAL en Cosmos DB NoSQL (no mock)."""
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from app.settings import Settings
from datetime import datetime, timezone
from uuid import uuid4

def persist_ticket(payload):
    cfg=Settings.read()
    client=CosmosClient(cfg.cosmos_endpoint,credential=DefaultAzureCredential())
    container=client.get_database_client(cfg.cosmos_database).get_container_client(cfg.cosmos_container)
    item={**payload.model_dump(exclude={'approved'}), 'id':str(uuid4()),
          'status':'open','created_at':datetime.now(timezone.utc).isoformat(),
          'origin':'enterprise-masterclass-demo'}
    # Si hay un error se eleva y el frontend nunca comunica que se ha creado.
    created=container.create_item(body=item)
    return {'id':created['id'],'status':created['status'],'category':created['category'],
            'priority':created['priority'],'created_at':created['created_at']}

def read_ticket(ticket_id: str):
    cfg=Settings.read()
    client=CosmosClient(cfg.cosmos_endpoint,credential=DefaultAzureCredential())
    container=client.get_database_client(cfg.cosmos_database).get_container_client(cfg.cosmos_container)
    return container.read_item(item=ticket_id,partition_key=ticket_id)
