# AI Fundamentals for Enterprise — Clase 3

## Agente de soporte empresarial (Python + Microsoft Foundry + Agent Framework)

Repositorio para el laboratorio de la tercera clase. Las consultas RAG utilizan Azure AI Search, el agente consulta un modelo real de Microsoft Foundry y las escrituras autorizadas se almacenan en Azure Cosmos DB for NoSQL. Incluye los archivos del laboratorio de la Clase 2 bajo `rag_clase2/` para reutilizar Blob Storage, indexación y búsquedas.

**Importante:** hemos implementado un *agente local en el proceso* usando Microsoft Agent Framework y `FoundryChatClient` (Responses API); **no** desplegamos un agente hospedado en Foundry Agent Service. 

El backend FastAPI y la UI son locales, no tienen autenticación corporativa, y no deben exponerse en Internet sin mejoras.

Se incorpora **un servidor MCP real Streamable HTTP** (`mcp_server/server.py`) para consultar Azure AI Search y descubrir categorías. Microsoft Agent Framework se conecta mediante `MCPStreamableHTTPTool`. La escritura de tickets **no está expuesta por MCP** y sigue dependiendo de aprobación humana y FastAPI/Cosmos DB. Consulta [docs/MCP.md](docs/MCP.md).

## Arquitectura

```text
DOCS Markdown -> (upload_samples) -> Azure Blob Storage [privado]
                                      |  (ingest desde Python, Clase 2)
                                      v
                          Foundry embeddings -> Azure AI Search
                                                   ^
                                                   | search_knowledge() vía MCP
Usuario -> Streamlit -> Agent Framework + cliente MCP -> Foundry Responses API
                           | propose_ticket() (SOLO propuesta)
                           v
                   Pantalla de aprobación humana
                           | usuario aprueba en UI
                           v
             FastAPI POST /tickets (validación + API key local)
                           v
                     Azure Cosmos DB NoSQL
```

## Requisitos

- Python 3.11+ y Azure CLI (`az login`)
- Proyecto Microsoft Foundry con deployment de chat compatible con Responses API/function calling y otro de embeddings (mismos que Clase 2)
- Azure AI Search, Blob Storage y índice con **los documentos de Clase 2**
- Azure Cosmos DB NoSQL (se proporciona Bicep); permisos de **plano de datos** Cosmos DB para la identidad local
- Región y capacidad de la suscripción que admitan los servicios elegidos; su consumo puede generar costos
- Para probar **Prompt Shields y moderación**, un recurso Azure AI Content Safety opcional (endpoint y clave)

## Inicio rápido (bash, macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
az login
```

1. Completa `.env` usando un único archivo en la raíz. Puedes usar los recursos Search y Blob Storage de la Clase 2. El índice debe existir antes de iniciar el agente.
2. Inicia también el servidor MCP en una tercera terminal (antes de ejecutar el agente):

```bash
python -m mcp_server.server
```

3. Si necesitas preparar la búsqueda desde cero, ejecuta **desde la raíz**:

```bash
python -m rag_clase2.scripts.upload_samples
python -m rag_clase2.scripts.ingest
```

4. Crear Cosmos DB NoSQL (si aún no existe):

```bash
export AZURE_RESOURCE_GROUP=masterclass-dia1-rg
export AZURE_LOCATION=swedencentral
export COSMOS_ACCOUNT_NAME=cosmos-clase3-xyz123
bash infra/deploy-cosmos.sh

# Asigna el rol de DATOS al usuario actual, requiere privilegios para la asignación:
bash infra/assign-cosmos-role.sh
```

Copia `cosmosEndpoint` a `COSMOS_ENDPOINT` en `.env`. Cosmos puede tardar en propagar permisos.

Valida el protocolo y el descubrimiento de herramientas: 

```python
python -m scripts.check_mcp
```

5. Configura `TICKET_API_KEY` con un secreto de larga longitud (por ejemplo, `python -c "import secrets; print(secrets.token_urlsafe(32))"`). 

Usarás **tres terminales** (MCP + API + UI), ambas con `.venv` activado y desde la raíz.

```bash
# Terminal A: API que persiste en Cosmos DB
uvicorn backend.api:api --host 127.0.0.1 --port 8070

# Terminal B: comprobación y UI
python -m scripts.check_connections
python -m streamlit run app/main.py
```

La aplicación se abrirá normalmente en `http://localhost:8501`. 

Los pasos completos están en [docs/AZURE_SETUP.md](docs/AZURE_SETUP.md) y ejemplos de uso en [docs/DEMO.md](docs/DEMO.md).

## Demostraciones

| Demo | Ejemplo | Comportamiento verificable |
|---|---|---|
| 1. RAG | ¿Cómo reportar un incidente? | Invoca `search_knowledge`, muestra fuentes, no escribe tickets |
| 2. Acción | No puedo iniciar sesión, crea un ticket | Invoca `propose_ticket` y devuelve propuesta; requiere **clic explícito** de aprobación |
| 3. Error | Solicitud incompleta / forzar escritura | Debe pedir detalles y no escribir sin aprobación; la API puede devolver errores reales |
| 4. Safety (opcional) | Instrucción maliciosa en prompt o documento | Si Content Safety está configurado, Prompt Shields detecta o no el intento real |

## Seguridad y límites

- No se almacena nada en Cosmos a través de herramientas invocadas directamente por el agente: `propose_ticket` solo prepara datos.
- El frontend ofrece un paso de confirmación; el backend requiere `approved: true` y una API key. **Esto demuestra el flujo de aprobación, pero NO es una garantía de autorización**: un usuario que conozca la API key podría falsificar el campo `approved`. En producción: Entra ID, identidad del aprobador, autorización verificable del servidor, auditoría y mecanismos antifraude.
- La API solo escucha `127.0.0.1` en el tutorial. Nunca expongas `TICKET_API_KEY` en repositorios ni actives CORS público sin autenticación.
- Prompt Shields y análisis de contenido son opcionales. Si no se configura el recurso, la UI no debe describirse como protegida por esos filtros. Si está configurado, el flujo **bloquea** cuando una detección o error de red ocurre; no presupongas efectividad perfecta.
- Los documentos RAG se tratan como datos de baja confianza. No hay autorización por documento en este demo; usa documentos ficticios.
- El pipeline de Clase 2 usa una clave administrativa de Search solo para el laboratorio. Para producción usa identidades administradas, roles mínimos y separa credenciales de ingesta/consulta.

## Estructura

```text
app/            Interfaz, agente, propuesta local, validaciones, safety
mcp_server/     Servidor MCP 2.x Streamable HTTP (solo lectura)
backend/        API FastAPI y persistencia real Cosmos DB
infra/          Bicep + scripts RBAC Cosmos DB
scripts/        Comprobaciones y evaluaciones
rag_clase2/     Fuente de documentos, Blob Storage, Search y embeddings (Clase 2)
docs/           Guía Azure, instructor, participante, seguridad/evaluación
```

## Documentación de Microsoft

- [Agent Framework + FoundryChatClient](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/model-providers/microsoft-foundry)
- [Quickstart Agent Framework](https://learn.microsoft.com/en-us/agent-framework/get-started/your-first-agent)
- [Cosmos DB Python](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/quickstart-python)
- [Content Safety Prompt Shields](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/quickstart-jailbreak)
- [Content Safety análisis de texto](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/quickstart-text)
