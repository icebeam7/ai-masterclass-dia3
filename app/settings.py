from dataclasses import dataclass
import os
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class Settings:
    endpoint: str
    model: str
    cosmos_endpoint: str
    cosmos_database: str
    cosmos_container: str
    api_url: str
    api_key: str
    mcp_url: str

    @classmethod
    def read(cls):
        names = ['AZURE_AI_PROJECT_ENDPOINT','AZURE_AI_MODEL_DEPLOYMENT_NAME',
                 'COSMOS_ENDPOINT','TICKET_API_KEY']
        missing=[k for k in names if not os.getenv(k) or os.getenv(k,'').startswith(('CAMBIAR_','https://RECURSO','https://TU-'))]
        if missing: raise ValueError('Configura las variables: '+', '.join(missing))
        return cls(os.environ['AZURE_AI_PROJECT_ENDPOINT'], os.environ['AZURE_AI_MODEL_DEPLOYMENT_NAME'],
                   os.environ['COSMOS_ENDPOINT'], os.getenv('COSMOS_DATABASE','enterprise-support'),
                   os.getenv('COSMOS_CONTAINER','tickets'), os.getenv('TICKET_API_URL','http://127.0.0.1:8070'),
                   os.environ['TICKET_API_KEY'],
                   os.getenv('MCP_SERVER_URL','http://127.0.0.1:8001/mcp'))
