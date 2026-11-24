# Laboratorio MCP — Clase 3

## Qué demuestra MCP

**Model Context Protocol (MCP)** es un protocolo abierto que permite a clientes de IA descubrir e invocar herramientas o acceder a recursos de servidores. Aquí exponemos un **servidor MCP real** mediante el SDK Python oficial 2.x, con transporte **Streamable HTTP**.

| Herramienta MCP | Origen | Efecto |
|---|---|---|
| `search_knowledge(question)` | Azure AI Search, índice generado desde Azure Blob Storage | Solo lectura; recuperación real |
| `get_ticket_categories()` | Reglas empresariales del backend | Solo lectura; categorías y prioridades |

`propose_ticket` se mantiene como herramienta **local** de Agent Framework para conservar la propuesta aprobable en Streamlit. **MCP no escribe tickets.** La escritura real se realiza únicamente mediante FastAPI y Cosmos DB tras confirmación explícita del usuario.

## Instalación

Desde la raíz del repositorio y con `.venv` activo:

```bash
pip install -r requirements.txt
cp .env.example .env  # si aún no existe
az login
```

Configura Foundry, Azure AI Search, Blob Storage y Cosmos según `docs/AZURE_SETUP.md`. Usa:

```dotenv
MCP_SERVER_URL=http://127.0.0.1:8001/mcp
MCP_PORT=8001
```

## Levantar los tres procesos

**Terminal A — Servidor MCP (puerto 8001):**

```bash
python -m mcp_server.server
```

**Terminal B — API persistencia Cosmos (puerto 8070):**

```bash
uvicorn backend.api:api --host 127.0.0.1 --port 8070
```

**Terminal C — Inspección MCP, comprobación y UI:**

```bash
python -m scripts.check_mcp
python -m scripts.check_connections
python -m streamlit run app/main.py
```

La comprobación de `scripts.check_mcp` realiza **handshake MCP**, `tools/list` y `tools/call` con el servidor local real (sin Azure para la consulta de categorías). Una consulta de `search_knowledge` sí necesita Azure AI Search y el deployment de embeddings.

## Demostración en vivo

1. Enseña `mcp_server/server.py`, donde se registran herramientas con `@mcp.tool()`.
2. Ejecuta `python -m scripts.check_mcp` y observa `search_knowledge` y `get_ticket_categories` descubiertas dinámicamente.
3. En Streamlit, ejecuta una pregunta de políticas. El agente utiliza MCP para acceder a Search. Comprueba `results/mcp_calls.jsonl` o el panel de registro MCP.
4. Pide crear un ticket. El agente utiliza la herramienta local `propose_ticket`, no una escritura MCP.
5. Confirma en Streamlit y muestra el documento real en Cosmos DB.
6. Cambia la pregunta para ilustrar que el agente decide cuándo utilizar MCP; no hay garantía de que llame a una herramienta en todas las ejecuciones.

## Seguridad y límites

- Se sirve **solo en `127.0.0.1`**. No expongas el MCP sin OAuth, TLS, autorización por herramienta, límites de tasa y auditoría.
- El log local contiene solo metadatos de invocación (nombre de la herramienta, longitud de entrada, resultado), no las consultas completas.
- MCP no concede permisos; los permisos de Azure se aplican a la identidad del proceso servidor.
- Los fragmentos recuperados son datos no confiables; Prompt Shields es una capa adicional **opcional** cuando se configura Content Safety.
- El sistema de aprobación es didáctico. La API de tickets mantiene una clave compartida y una confirmación booleana, no identidad corporativa verificable.
- En modo real multiusuario, separar registros por tenant/usuario e introducir autorización a nivel documental.

## Referencias

- https://learn.microsoft.com/en-us/agent-framework/agents/tools/local-mcp-tools
- https://learn.microsoft.com/en-us/agent-framework/support/upgrade/migrate-to-mcp-2-x
- https://py.sdk.modelcontextprotocol.io/migration/
- https://modelcontextprotocol.io/specification/latest
