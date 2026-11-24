# Demo

**Demo 1: información:** selecciona la pregunta de procedimiento; pulsa **Ejecutar agente**. En `Trazas didácticas` observa `search_knowledge` vía MCP (registro en `results/mcp_calls.jsonl`), fuentes del documento y respuesta. Verifica que no existe propuesta de ticket.

**Demo 2: acción controlada:** selecciona solicitud de acceso. Ejecuta agente. Si el modelo prepara propuesta, observa `propose_ticket` y los datos. Revisa la edición de título/categoría/prioridad. Sin marcar confirmación, pulsa guardar: la UI lo impide. Marca aprobación y guarda: observa respuesta 201, ID real y registro en Cosmos DB Data Explorer.

**Demo 3: errores:** ejemplo de solicitud incompleta, después ejemplo de intento de saltar aprobación. Comprueba que el agente no puede acceder directamente a una operación de escritura. Si falla Cosmos, el backend responde error y nunca se muestra ticket creado.

**Evaluaciones y safety:** Si configuraste Content Safety, prueba Prompt Shields, los resultados pueden variar. 

**Preguntas:** ¿qué operación requiere aprobación? ¿qué métricas utilizarías para evaluar la herramienta RAG? ¿qué sucede si el documento contiene instrucciones maliciosas? ¿por qué un modelo no debe ser autoridad para conceder permisos?

