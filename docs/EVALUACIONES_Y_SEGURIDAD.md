# Evaluación, Content Safety y límites de seguridad

## Evaluación en este repo

La herramienta `search_knowledge` y `propose_ticket` registra eventos para inspección manual; esta bitácora no es una traza OpenTelemetry.

## Evaluaciones de agente para producción

| Métrica | Criterio sugerido |
|---|---|
| Task completion | Estado esperado del ticket y respuesta real de backend |
| Tool call accuracy | Uso de `search_knowledge` para información, `propose_ticket` para acción |
| Tool input accuracy | Categoría y prioridad correctas, límites de Pydantic |
| Groundedness | Respuesta RAG sustentada por fuentes citadas |
| Abstention | Declara falta de información cuando no hay evidencia |
| Safety pass rate | No ejecuta acciones no autorizadas, no filtra datos |
| Latencia/costo | Tiempo por ejecución, tokens y RU de Cosmos |

Para evaluaciones administradas de Foundry, registra datasets de preguntas y resultados y ejecútalos con las funciones de evaluación disponibles en tu versión del SDK/portal. **Este repositorio NO pretende afirmar que estas métricas se calculan automáticamente aquí.**

## Content Safety

Cuando se configura `CONTENT_SAFETY_ENDPOINT` y `CONTENT_SAFETY_KEY`:

- Prompt Shields detecta posibles inyecciones en prompt y documentos recuperados (`shieldPrompt`).
- Azure AI Content Safety analiza el contenido de entrada y salida en categorías Hate, SelfHarm, Sexual y Violence.
- Ante detección o error de red, la solicitud no continúa; la aplicación registra el error visible.

Si Content Safety no está configurado, **estas verificaciones externas no ocurren**. No confundas las instrucciones del agente con una barrera de seguridad. Ni Prompt Shields ni moderación garantizan 100% de detección.

## Threat model abreviado

- Prompt injection directo e indirecto desde Blob/Search.
- Exposición de documentos que el usuario no debería consultar: el laboratorio NO implementa autorización por documento.
- Acción no aprobada: el backend requiere campo de aprobación y token demo, pero **no verifica identidad de aprobador**.
- Confianza excesiva en argumentos sugeridos por el LLM.
- Errores de API y alucinación de éxito. La UI informa éxito solo tras respuesta HTTP 201.
- Escrituras duplicadas por reintentos: implementar idempotencia server-side para producción.

**Mejoras para producción:** autenticación Entra ID del usuario, autorización centralizada, identidad administrada por servicio, RBAC específico de cada recurso, aprobación persistida vinculada a identidad y solicitud, idempotency keys, límites por usuario, trazas OpenTelemetry / Azure Monitor, redes privadas, rotación de secretos, guardrails contra filtración de datos y un pipeline CI/CD de evaluaciones.
