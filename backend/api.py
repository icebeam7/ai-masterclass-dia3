"""FastAPI local para ticket; seguridad de ejemplo, NO autenticación enterprise."""
import hmac
from fastapi import FastAPI,Header,HTTPException
from app.settings import Settings
from app.tickets import ApprovedTicket,require_approval
from backend.cosmos import persist_ticket,read_ticket
from azure.cosmos.exceptions import CosmosResourceNotFoundError

api=FastAPI(title='Enterprise Support Ticket API',version='1.0.0')

def authenticate(key: str|None):
    expected=Settings.read().api_key
    if not key or not hmac.compare_digest(key,expected):
        raise HTTPException(status_code=401,detail='API key de demo inválida')

@api.get('/health')
def health():
    return {'status':'up','persistence':'Azure Cosmos DB NoSQL (no comprobada en /health)'}

@api.post('/tickets',status_code=201)
def create_ticket(ticket: ApprovedTicket,x_demo_api_key: str|None=Header(default=None)):
    authenticate(x_demo_api_key)
    try: require_approval(ticket)
    except PermissionError as exc: raise HTTPException(status_code=403,detail=str(exc)) from exc
    # En producción: aprobar usando identidad Entra y autorización server-side.
    try: return persist_ticket(ticket)
    except Exception as exc:
        raise HTTPException(status_code=502,detail=f'Cosmos DB no confirmó la creación: {type(exc).__name__}') from exc

@api.get('/tickets/{ticket_id}')
def get_ticket(ticket_id: str,x_demo_api_key: str|None=Header(default=None)):
    authenticate(x_demo_api_key)
    try:
        record=read_ticket(ticket_id)
        return {'id':record['id'],'title':record['title'],'status':record['status'],'category':record['category']}
    except CosmosResourceNotFoundError as exc:
        raise HTTPException(status_code=404,detail='No encontrado') from exc
