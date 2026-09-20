# Asistente Personal IA Local — Roadmap de desarrollo

> LOCAL FIRST — CLOUD WHEN NEEDED

Checklist consolidada a partir del roadmap aportado por el usuario. Se conservan las tareas completadas y pendientes; los ejemplos originales de arquitectura son orientativos, no requisitos de crear archivos anticipadamente.

## Evidencia y criterio de cierre

Revisión del 20 de septiembre de 2026: suite ejecutada por el agente, **22 passed en 2,52 s**, con bases temporales y sin consultas a proveedores. Las pruebas manuales de Ollama sin Internet y recuperación de recuerdos tras reiniciar fueron comunicadas por el usuario. Las marcas originales sobre otras pruebas manuales se conservan identificadas como tales, sin presentarlas como verificaciones nuevas.

Una tarea se completa con implementación, pruebas relevantes, manejo de errores, integración, documentación y comprensión del concepto cuando corresponda. La existencia de un archivo no completa su funcionalidad. No se hacen commits ni se implementan fases automáticamente.

**Corrección del alcance anterior:** están validados el contexto limitado y la memoria explícita clave-valor. Las fases 4 y 5 del roadmap completo siguen parcialmente pendientes. Las pruebas no prueban funcionalidades todavía inexistentes.

Cierre del bloque de eliminación: `/olvidar` implementado y validado con pruebas de persistencia, lógica del agente y consola simulada. Comprobación manual comunicada por el usuario. Conexiones SQLite cerradas explícitamente en todas las operaciones. Suite completa ejecutada por el agente: **28 passed en 1,91 s**, sin datos reales ni consultas a modelos.

## Objetivo final

- [x] Conversar de forma natural mediante el proveedor configurado; calidad no evaluada sistemáticamente.
- [x] Recordar información importante sobre mí mediante guardado explícito.
- [ ] Recordar proyectos, personas, preferencias y decisiones con estructura y relaciones propias.
- [ ] Recuperar conversaciones antiguas sin enviar todo el historial al LLM.
- [ ] Ejecutar acciones mediante herramientas.
- [ ] Trabajar con archivos locales.
- [ ] Consultar Internet cuando sea necesario.
- [ ] Gestionar calendario, correo y otras aplicaciones.
- [ ] Tener voz.
- [ ] Ejecutar automatizaciones.
- [x] Funcionar parcialmente o completamente sin Internet: conversación con Ollama validada por el usuario.
- [ ] Elegir automáticamente entre IA local y APIs externas.
- [ ] Minimizar el consumo de tokens mediante mediciones y optimización.
- [ ] Mantener todos los datos importantes localmente a medida que se incorporen nuevas funciones.

Historial y recuerdos actuales se almacenan en SQLite local. Si se usa OpenAI, el contexto y los recuerdos incluidos se envían al proveedor.

## Fase 0 — Base inicial

- [x] Python.
- [x] `main.py`.
- [x] `app/agente.py`.
- [x] `app/persistence/persistencia.py`.
- [x] SQLite.
- [x] Base `memoria.db` — funcionamiento verificado con bases temporales, sin inspeccionar datos reales.
- [x] Guardado del historial.
- [x] Recuperación de conversaciones como carga del historial; no búsqueda semántica.
- [x] Integración con GPT-5-nano en el proveedor OpenAI.
- [x] Variables sensibles mediante `.env`.
- [x] Separación inicial entre agente y persistencia.

El problema inicial de enviar todo el historial se ha corregido mediante selección de contexto. Sigue cargándose todo el historial al iniciar.

## Fase 1 — Arquitectura limpia

- [x] Crear `app/`.
- [x] Mover progresivamente la lógica.
- [x] Crear `config.py`.
- [x] Centralizar configuración fuera de la lógica; los límites de contexto son constantes de configuración.
- [x] Mantener `main.py` pequeño.

La clase real se llama `AgenteIA`. La persistencia vive en `app/persistence/`; no necesita trasladarse a `app/memoria/` para cumplir la separación. Los futuros módulos de memoria, herramientas y servicios se crearán cuando sean necesarios.

## Fase 2 — Desacoplar el LLM

- [x] Crear interfaz `LLMProvider` — método real `responder(messages)`.
- [x] Crear `OpenAIProvider`.
- [x] Mover allí el código de GPT-5-nano.
- [x] Instalar Ollama — validación manual comunicada.
- [x] Crear `OllamaProvider`.
- [x] Poder conversar usando GPT — marcado como probado por el usuario en el roadmap original; no repetido por el agente.
- [x] Poder conversar usando un modelo local — validación manual comunicada.
- [x] Elegir proveedor desde `.env`.

La interfaz permite sustituir proveedores. Gemini es una posibilidad futura; no está implementado.

## Fase 3 — IA local

- [x] Instalar Ollama — validación del usuario.
- [x] Descargar el primer modelo — validación del usuario.
- [x] Probarlo desde terminal — marcado por el usuario en el roadmap original.
- [x] Probarlo desde Python — validación del usuario.
- [x] Integrarlo con `OllamaProvider`.
- [x] Configurar el modelo local: el nombre real es `OLLAMA_MODEL`, no `LOCAL_MODEL`.
- [x] Ejecutar el asistente sin Internet — validación del usuario con `qwen3:4b`.
- [x] Comparar respuestas contra GPT-5-nano — marcado por el usuario en el roadmap original; sin benchmark reproducible disponible.

Mediciones futuras: tiempo hasta primera respuesta, tokens por segundo, RAM, VRAM, calidad y compatibilidad con herramientas. La ejecución local consume hardware y electricidad; también procesa tokens aunque no sean facturados por una API.

## Fase 4 — Gestión del contexto (parcial)

- [x] Separar historial y contexto enviado al modelo.
- [x] Mantener los últimos N mensajes activos en el contexto: se seleccionan hasta cinco turnos completos por defecto.
- [ ] Crear resumen de conversaciones antiguas.
- [ ] Guardar esos resúmenes.
- [x] Construir dinámicamente el contexto.
- [ ] Evitar cargar todo el historial de la BD automáticamente: `_cargar_historial()` todavía lo carga completo.

El límite actual es de 12000 caracteres, no tokens. Se conservan sistema y pregunta actual, se excluyen preguntas anteriores sin respuesta y se retiran primero turnos antiguos. Los recuerdos cuentan en el límite. Una base excesiva se rechaza antes de guardar la pregunta o llamar al LLM. El historial completo permanece en SQLite y `self.messages`.

La arquitectura objetivo combina sistema, perfil relevante, resúmenes, recuerdos seleccionados, turnos recientes y pregunta actual. Resúmenes y selección semántica todavía no existen. La lógica actual reside en `agente.py`; crear `historial.py` o `context_manager.py` dependerá de la necesidad de separar responsabilidades.

## Fase 5 — Memoria real (parcial)

- [x] Diseñar memoria estructurada básica: clave-valor, separada del historial.
- [x] Crear tabla de recuerdos: se llama `memoria`, no `memorias`.
- [ ] Añadir categorías.
- [x] Crear memorias mediante `/recordar clave=valor`.
- [x] Modificarlas repitiendo la clave.
- [x] Eliminarlas mediante `eliminar_memoria` y `/olvidar clave`, con validación y pruebas de consola.
- [x] Consultarlas mediante `obtener_memoria` y `cargar_memoria`; se integran en el contexto.
- [ ] Añadir importancia.
- [x] Evitar guardado automático de información irrelevante: solo se guarda lo solicitado explícitamente; no hay clasificador de relevancia.

La memoria inmediata corresponde al contexto reciente. La memoria episódica futura representará acontecimientos o conversaciones; la información estable incluirá preferencias, proyectos, personas y lugares. Aún no hay entidades ni relaciones propias para estos tipos.

Posibles ampliaciones de esquema: categoría, importancia, fechas de creación y actualización. Las tablas `conversaciones`, `preferencias`, `proyectos`, `personas` y `resumenes` son propuestas futuras, no requisitos de crearlas todas ahora. En esta fase, “memoria semántica” como información estable no equivale todavía a búsqueda con embeddings.

## Fase 6 — Memoria semántica con embeddings

- [ ] Instalar modelo de embeddings.
- [ ] Generar embeddings localmente.
- [ ] Guardarlos.
- [ ] Implementar similitud semántica.
- [ ] Recuperar Top-K memorias.
- [ ] Añadir únicamente esas memorias al prompt.

Flujo previsto: pregunta → embedding → búsqueda → recuerdos relevantes → contexto → LLM. Top-K será un máximo; puede no haber recuerdos relevantes. Candidatos del roadmap original: EmbeddingGemma y Qwen3-Embedding. Se comprobarán documentación, español, recursos y rendimiento antes de elegir. No hay modelo seleccionado ni instalado para esta fase.

## Fase 7 — Herramientas

- [ ] Crear clase base Tool.
- [ ] Crear ToolRegistry.
- [ ] Primera herramienta: fecha/hora.
- [ ] Herramienta de sistema.
- [ ] Herramienta de archivos.
- [ ] Manejar errores.
- [ ] Registrar ejecución.
- [ ] Pedir confirmación para operaciones peligrosas.

El modelo propone una acción; código Python autorizado la ejecuta. Ejemplos futuros: fecha, hora, lectura, creación y búsqueda de archivos, abrir programas, recordatorios y clima. El soporte deberá validarse con el modelo elegido.

## Fase 8 — Personalización

- [ ] Crear perfil.
- [ ] Crear preferencias como estructura propia.
- [ ] Detectar nuevas preferencias.
- [ ] Permitir modificarlas.
- [ ] Relacionar memorias con proyectos.
- [ ] Relacionar personas.
- [ ] Relacionar lugares.
- [ ] Crear prioridades.

Recuperar solo la parte relevante del perfil. La detección futura no cambia ahora el guardado explícito de recuerdos.

## Fase 9 — Router inteligente de modelos

- [x] Crear `router.py`: existe la selección estática; no implica routing inteligente.
- [ ] Clasificar peticiones.
- [ ] Detectar cuándo no hace falta IA.
- [x] Modelo local por defecto en configuración.
- [ ] GPT como fallback.
- [ ] Registrar qué modelo resolvió cada petición.
- [ ] Registrar consumo API.
- [ ] Poder definir límite mensual.

Opciones futuras: Python directo, modelo local pequeño, modelo local potente o API externa. Considerar calidad, privacidad, latencia, recursos y coste. Actualmente un fallo no provoca cambio automático de proveedor.

## Fase Q — Formación en computación cuántica y optimización híbrida

Pausa temporal del desarrollo funcional después de la Fase 9 y antes de la Fase 10. Aprender con recursos oficiales, principalmente IBM Quantum y Qiskit. Proyectos independientes, orientados a GitHub/CV y problemas reales; no añadir cuántica por marketing.

- [ ] Estudiar funciones objetivo, restricciones, variables binarias, QUBO e Ising.
- [ ] Aprender Qiskit, algoritmos variacionales y QAOA.
- [ ] Trabajar con simuladores, ruido, limitaciones y transpilación.
- [ ] Ejecutar en hardware real cuando sea razonable.
- [ ] Comparar algoritmos clásicos y cuánticos y construir workflows híbridos.
- [ ] Q1: formular Max-Cut, resolverlo clásicamente, convertirlo a QUBO/Ising, ejecutar QAOA en simulador y comparar resultados.
- [ ] Q2: optimizar asignación de tareas a Python, modelos locales pequeños/grandes y API considerando coste, latencia, RAM, VRAM, calidad estimada y privacidad; formular, crear baseline clásico, QUBO y comparación QAOA.
- [ ] Q3: scheduler CPU/GPU/local/cloud con prioridades, duración, RAM, VRAM, plazos y coste; comparar tiempo total, costes, incumplimientos y eficiencia de recursos entre soluciones clásicas e híbridas.
- [ ] Q4: ampliar Q2 o Q3 con warm-start QAOA, optimizadores clásicos, profundidades, ruido, transpilación, hardware real y benchmarking.
- [ ] Cada proyecto incluye `README.md`, `src/`, `notebooks/`, `tests/`, `results/` y `requirements.txt`.
- [ ] Documentar problema, formulación, soluciones clásica y cuántica, instancias, metodología, métricas, resultados, gráficas, limitaciones, conclusiones y reproducción.

Nunca afirmar una ventaja cuántica sin demostrarla experimentalmente. El aprendizaje y la metodología experimental son resultados válidos aunque gane el método clásico.

## Fase 10 — Estrategia de costes

- [ ] Medir costes de hardware y electricidad de la ejecución local.
- [ ] Evaluar OpenAI como fallback y verificar precios oficiales al realizar los cálculos.
- [ ] Evaluar Gemini como proveedor opcional, comprobando cuotas y tratamiento de datos del servicio elegido.
- [ ] Comparar coste, calidad y privacidad con contexto reducido.

Las tarifas y ofertas del texto original son referencias históricas no verificadas aquí; no se presentan como precios actuales. La prioridad es evitar contexto innecesario y mantener datos sensibles bajo control.

## Fase 11 — Internet

- [ ] Crear servicio HTTP.
- [ ] Añadir primera API externa.
- [ ] Gestionar errores.
- [ ] Gestionar ausencia de Internet.
- [ ] Implementar timeout.
- [ ] Implementar caché.

Herramientas previstas: búsqueda web, clima, noticias y mapas. Preferir APIs específicas para obtener hechos actuales y usar el LLM solo cuando aporte valor a su interpretación.

## Fase 12 — Archivos y documentos personales

- [ ] Indexar carpetas autorizadas.
- [ ] TXT.
- [ ] PDF.
- [ ] DOCX.
- [ ] Markdown.
- [ ] Buscar por nombre.
- [ ] Buscar por contenido.
- [ ] Búsqueda semántica.
- [ ] Detectar documentos modificados.

Flujo previsto: carpetas → extracción de texto → embeddings → almacenamiento/búsqueda vectorial. Ejemplos: localizar facturas, encontrar importes y resumir documentos.

## Fase 13 — Integraciones

- [ ] Calendario.
- [ ] Correo.
- [ ] Drive.
- [ ] Servicios adicionales.
- [ ] OAuth.
- [ ] Sistema de permisos.
- [ ] Confirmación antes de modificar datos.

Servicios candidatos: Google Calendar, Gmail, Google Drive, Notion, GitHub y Home Assistant.

## Fase 14 — Voz

- [ ] Speech-to-Text local.
- [ ] Detectar inicio/final de voz.
- [ ] Enviar texto al agente.
- [ ] TTS local.
- [ ] Interrumpir respuesta.
- [ ] Wake word opcional.

Flujo: micrófono → transcripción → agente → síntesis → altavoces. Se aborda después de memoria y herramientas.

## Fase 15 — Interfaz gráfica

- [ ] Estabilizar el backend.
- [ ] Evaluar una API local para separar interfaz y lógica.
- [ ] Comparar PySide6, Tauri, Electron y web local según necesidades.
- [ ] Implementar la interfaz elegida.

No construir la interfaz anticipadamente. El orden entre interfaz y automatización se concretará según dependencias reales.

## Fase 16 — Automatizaciones

- [ ] Scheduler.
- [ ] Tareas recurrentes.
- [ ] Tareas únicas.
- [ ] Eventos.
- [ ] Notificaciones.
- [ ] Historial de ejecuciones.
- [ ] Reintentos.
- [ ] Límites.

Flujo: scheduler → evento → agente → herramientas. Ejemplos: revisión de calendario, comprobaciones periódicas y procesamiento de nuevos archivos.

## Fase 17 — Seguridad

- [ ] Sistema de permisos.
- [ ] Lista blanca de carpetas.
- [ ] Lista blanca de aplicaciones.
- [ ] Confirmaciones.
- [ ] Registro de acciones.
- [ ] Backups.
- [x] Configuración de secretos mediante `.env`, sin credenciales incrustadas en el código revisado.
- [x] No proporcionar claves API al LLM en el flujo actual; mantener esta propiedad en herramientas e integraciones futuras.

Clasificar acciones de lectura, modificación y peligrosas. Aplicar permisos y confirmaciones desde la introducción de herramientas, sin esperar a esta fase. No se han inspeccionado los secretos reales.

## Fase 18 — Tests, logs y métricas

- [ ] Logging.
- [x] Tests de persistencia.
- [x] Tests de memoria explícita y contexto; ampliar para futuras funciones.
- [ ] Tests de herramientas.
- [ ] Tests de proveedores: existen tests de selección del router, faltan respuestas y errores simulados de los adaptadores.
- [ ] Métricas de latencia.
- [ ] Métricas de tokens.
- [ ] Métricas de coste.

Registrar progresivamente modelo, herramientas, errores, recuerdos recuperados y consumos. Las pruebas acompañan cada fase; no se posponen hasta la 18.

## Arquitectura objetivo

Usuario → interfaz de texto/voz → agente/orquestación → memoria, herramientas y router.

- Memoria: SQLite, vectores y perfil.
- Herramientas: sistema, web y aplicaciones.
- Proveedores: Ollama, OpenAI y posibles alternativas.

Es una visión futura. La arquitectura actual tiene consola, agente, persistencia SQLite y proveedores seleccionados por configuración.

## Orden de implementación — etapas del roadmap original

Las etapas son agrupaciones, no equivalen a los números de fase.

### Etapa 1 — Base

- [x] Agente básico.
- [x] OpenAI.
- [x] SQLite.
- [x] Historial.
- [x] Persistencia separada.

### Etapa 2 — Proveedores

- [x] Reorganizar arquitectura.
- [x] Crear `LLMProvider`.
- [x] Crear `OpenAIProvider`.
- [x] Instalar Ollama — validación del usuario.
- [x] Crear `OllamaProvider`.
- [x] Cambiar entre local/OpenAI mediante configuración.

### Etapa 3 — Contexto (parcial)

- [x] Context manager: lógica existente en `_construir_contexto`.
- [ ] Resúmenes.
- [x] No enviar historial completo cuando excede los límites.
- [ ] Control de tokens: hay control de caracteres.

### Etapa 4 — Memoria (parcial)

- [x] Memoria estructurada básica clave-valor.
- [ ] Preferencias como entidad propia.
- [ ] Proyectos.
- [ ] Personas.
- [x] Memoria a largo plazo explícita en SQLite.

### Etapa 5 — Recuperación semántica

- [ ] Embeddings locales.
- [ ] Búsqueda semántica.
- [ ] RAG de memorias.

### Etapa 6 — Herramientas

- [ ] Tools.
- [ ] Tool registry.
- [ ] Archivos.
- [ ] Sistema.
- [ ] Internet.

### Etapa 7 — Routing

- [ ] Router inteligente de modelos.
- [ ] Política local-first automática por petición; ya existe proveedor local predeterminado.
- [ ] GPT fallback.
- [ ] Control de costes.

La pausa de la Fase Q se sitúa tras el router inteligente, antes de continuar el desarrollo funcional.

### Etapa 8 — Documentos

- [ ] Indexación de documentos.
- [ ] PDFs.
- [ ] Documentos personales.
- [ ] Búsqueda semántica.

### Etapa 9 — Aplicaciones

- [ ] Calendario.
- [ ] Email.
- [ ] Drive.
- [ ] Aplicaciones.

### Etapa 10 — Interacción y ejecución continua

- [ ] Voz.
- [ ] Interfaz gráfica.
- [ ] Automatizaciones.
- [ ] Servicio ejecutándose constantemente.

## Coste y aprendizaje

Preferencia cuando tenga sentido: Python → datos locales → herramientas → modelos locales → APIs gratuitas/específicas → APIs LLM de pago. Embeddings, conversación y clasificación locales evitan tokens API, no cómputo ni consumo eléctrico. Medir antes de optimizar.

Competencias buscadas: Python, Git, testing, arquitectura, APIs, LLMs, Ollama, embeddings, RAG, bases de datos, algoritmos, optimización, profiling, benchmarking, Qiskit y experimentación híbrida reproducible.

Trabajar por micro-pasos: objetivo, concepto, arquitectura, archivos afectados, tarea pequeña, revisión y prueba. El usuario escribe el código por defecto. Al cerrar una fase, resumir lo construido, aprendido, arquitectura, pruebas, deuda y siguiente fase.
