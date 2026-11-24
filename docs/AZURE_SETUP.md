# Preparación completa de Azure — Clase 3

## 1. Autenticarse

```bash
az login
az account set --subscription "SUBSCRIPTION_ID"
```

Necesitas una cuenta de Azure con permisos para crear recursos y asignar roles de datos. Los nombres deben ser globalmente únicos cuando aplique.

## 2. Recuperar Foundry, Search y Blob Storage de la Clase 2

Si ya completaste la Clase 2, **reutiliza** el endpoint del proyecto, el deployment de chat, el de embeddings, el índice `AZURE_SEARCH_INDEX` y el contenedor Blob. Copia los valores a `.env` en **la raíz de este proyecto**.

Si no tienes el índice preparado, sigue `rag_clase2/docs/AZURE_SETUP.md` y ejecuta:

```bash
python -m rag_clase2.scripts.upload_samples
python -m rag_clase2.scripts.ingest
```

Estas operaciones leen documentos desde Blob Storage y crean embeddings + índice en Azure AI Search. El almacenamiento local solo sirve como material de carga inicial.

**Nota de SDK:** según el modelo, las llamadas a embeddings pueden requerir deployment OpenAI compatible. Ajusta el nombre al deployment REAL en Foundry. La aplicación no genera respuestas simuladas.

## 3. Desplegar Azure Cosmos DB

```bash
export AZURE_RESOURCE_GROUP=masterclass-dia1-rg
export AZURE_LOCATION=eastus
export COSMOS_ACCOUNT_NAME=cosmos-clase3-unico123
bash infra/deploy-cosmos.sh
```

Bicep crea un Cosmos DB for NoSQL **serverless** con `enterprise-support/tickets`, clave de partición `/id`, autenticación local deshabilitada. Si tu región/suscripción no admite serverless, modifica la capacidad antes de desplegar o crea cuenta manual con contenedor equivalente. La cuenta queda con acceso de red público para facilitar el laboratorio, **no es configuración final de producción**.

Asignar rol de datos al usuario que ejecutará FastAPI:

```bash
bash infra/assign-cosmos-role.sh
```

Si se usa una identidad administrada, establece `PRINCIPAL_ID=<object-id>` antes del script. El rol de Azure Resource Manager Contributor **no** equivale a permisos de datos de Cosmos DB. Puede existir un período de propagación. Verifica que el principal coincide con la identidad que selecciona `DefaultAzureCredential`.

## 4. Variables principales de .env

```dotenv
AZURE_AI_PROJECT_ENDPOINT=https://RECURSO.services.ai.azure.com/api/projects/PROYECTO
AZURE_AI_MODEL_DEPLOYMENT_NAME=DEPLOYMENT_CHAT
AZURE_AI_EMBEDDING_DEPLOYMENT_NAME=DEPLOYMENT_EMBEDDINGS
AZURE_SEARCH_ENDPOINT=https://SERVICIO.search.windows.net
AZURE_SEARCH_INDEX=enterprise-knowledge-v1
AZURE_SEARCH_ADMIN_KEY=CLAVE_DEL_SERVICIO
AZURE_STORAGE_ACCOUNT_URL=https://CUENTA.blob.core.windows.net
AZURE_STORAGE_CONTAINER=enterprise-documents
COSMOS_ENDPOINT=https://COSMOS.documents.azure.com:443/
COSMOS_DATABASE=enterprise-support
COSMOS_CONTAINER=tickets
TICKET_API_URL=http://127.0.0.1:8070
TICKET_API_KEY=TOKEN_LARGO_ALEATORIO
```

## 5. Content Safety opcional pero real

Crea un recurso Azure AI Content Safety compatible con la región y suscripción. En la página de claves y endpoint copia a `.env`:

```dotenv
CONTENT_SAFETY_ENDPOINT=https://TU-CONTENT-SAFETY.cognitiveservices.azure.com
CONTENT_SAFETY_KEY=CLAVE_DEL_RECURSO
CONTENT_SAFETY_THRESHOLD=4
```

Con ambos valores definidos, `app/safety.py` llama de verdad a **Prompt Shields REST (2024-09-01)** en el prompt y en documentos recuperados, y **Analyze Text** en entrada y salida. Si una llamada falla, la ejecución también falla (fail closed). Sin ambos valores no hay análisis externo. Prompt Shields no sustituye permisos ni validaciones. Algunos límites dependen de la región y tamaño de texto.

## 6. Ejecutar

```bash
uvicorn backend.api:api --host 127.0.0.1 --port 8070
# terminal independiente:
python -m scripts.check_connections
python -m streamlit run app/main.py
```

## 7. Problemas comunes

- **403 Cosmos:** el principal no tiene rol de datos o la asignación no se propagó.
- **401 Foundry:** `az login`, proyecto erróneo o permisos insuficientes.
- **404 deployment:** nombre en `.env` diferente al nombre del deployment de Foundry.
- **Dimensión vectorial distinta:** usa el mismo embedding deployment y `EMBEDDING_DIMENSIONS` de Clase 2.
- **API 502:** Cosmos no confirmó escritura; consultar el log FastAPI y comprobar rol.
- **Puerto ocupado:** detén el servicio existente o actualiza `TICKET_API_URL`.
- **Content Safety HTTP 403/404:** verifica endpoint, clave, región y disponibilidad de la característica.

## 8. Limpieza

Los recursos de Azure generan costos; elimina solo el grupo de recursos que creaste exclusivamente para este laboratorio. Si el grupo contiene recursos compartidos, elimina componentes de forma individual. `az group delete -n <grupo>` es destructivo.

## Servidor MCP

Desde la raíz: `python -m mcp_server.server`. En otra terminal `python -m scripts.check_mcp`. Revisa [MCP.md](MCP.md). La búsqueda real necesita recursos configurados; el MCP permanece solo en loopback.
