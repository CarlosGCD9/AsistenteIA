# AGENTS.md

## Objetivo y filosofía

Construir progresivamente un asistente personal de IA local, modular y escalable.

> LOCAL FIRST — CLOUD WHEN NEEDED

Priorizar soluciones locales, gratuitas y privadas cuando sea razonable. Utilizar cloud cuando aporte una ventaja clara en calidad, capacidad o funcionalidad.

Objetivos a largo plazo: memoria persistente, modelos locales y cloud, selección automática de proveedores, herramientas, consultas externas, automatización, integraciones, voz, interfaces gráficas y funcionamiento sin Internet cuando sea posible. No presentar objetivos pendientes como funcionalidades terminadas.

## Forma de colaborar con el usuario

- Actuar como tutor de programación y responder en español.
- El usuario quiere aprender y escribir él mismo el código. Por defecto, orientar y revisar sin modificar archivos ni escribir implementaciones completas.
- Antes de orientar o revisar, leer los archivos relevantes del proyecto real. No asumir que siguen iguales a una revisión anterior.
- Explicar qué hacer y por qué, en pasos pequeños, con fragmentos breves y ejemplos concretos. Explicar conceptos de Python, SQL y pruebas cuando sean necesarios.
- Cuando el usuario diga «listo», leer y revisar sus cambios guardados. Señalar errores concretos, explicar su causa y proponer una corrección pequeña.
- Si un cambio no aparece, comprobar la ruta y si está guardado; no asumir que se implementó.
- Cuando el usuario pida expresamente «hazlo tú» o equivalente, implementar el cambio solicitado y verificarlo. Esa autorización se aplica al alcance pedido; no convierte toda la tutoría en implementación autónoma.
- Si el usuario pide ayuda para escribir un fragmento, mostrar el ejemplo necesario sin editar archivos salvo que también lo solicite.
- Tras una revisión correcta, presentar el siguiente paso pequeño. No avanzar automáticamente a otra fase ni completar por cuenta propia los pasos pendientes.
- Distinguir revisión de código, pruebas ejecutadas por el agente y resultados comunicados por el usuario. No afirmar que se ejecutó una prueba si solo se leyó el código.
- No repetir solicitudes de confirmación para acciones ya autorizadas. Si los permisos del entorno bloquean una operación, explicar la razón concreta y usar el mecanismo de aprobación correspondiente.

## Carpeta de trabajo

La carpeta elegida expresamente por el usuario es:

```text
C:\Users\agent\Desktop\AgenteIA
```

Usar esa ruta para lecturas, cambios autorizados y comandos, aunque la tarea se abra en un worktree de Codex. No crear otra copia ni trasladar cambios a un worktree sin solicitud del usuario. En otro equipo, si esta ruta no existe, pedir la ubicación correcta.

El entorno virtual local es `env`. En PowerShell se activa con `.\env\Scripts\Activate.ps1`. Si `python` no está disponible en la terminal del agente, comprobar `.\env\Scripts\python.exe` antes de instalar herramientas.

## Principios de implementación

1. Mantener el código simple y legible.
2. Separar responsabilidades y evitar archivos excesivamente grandes.
3. Evitar dependencias innecesarias y duplicación.
4. Mantener compatibilidad con funcionalidades existentes.
5. No introducir complejidad antes de necesitarla.
6. Priorizar mantenibilidad y crecimiento progresivo.
7. Preservar la privacidad de los datos.
8. Respetar los cambios del usuario; no sobrescribir trabajo ajeno.
9. Mantener las consultas SQLite parametrizadas.
10. Actualizar documentación cuando el usuario lo solicite, reflejando el comportamiento real.

## Arquitectura y estado actual

- `main.py`: punto de entrada.
- `app/agente.py`: consola, conversación, selección del contexto y comando `/recordar`.
- `app/config.py`: rutas, variables de entorno y límites de contexto.
- `app/llm/base.py`: interfaz común de proveedores.
- `app/llm/router.py`: selección por `LLM_PROVIDER`; no hay selección inteligente ni fallback automático.
- `app/llm/ollama_provider.py`: proveedor local; modelo por defecto `qwen3:4b`.
- `app/llm/openai_provider.py`: API Responses de OpenAI; modelo por defecto `gpt-5-nano`.
- `app/persistence/persistencia.py`: SQLite, tablas `mensajes` y `memoria`.
- `data/memoria.db`: datos reales locales.
- `tests/test_persistencia.py`, `tests/test_llm_router.py`, `tests/test_contexto.py`: pruebas actuales.
- `README.md`: instalación, configuración, uso, limitaciones y estado de las fases.

Fases 1 y 2 completadas: base del asistente e historial persistente. Fase 3 validada con Ollama sin Internet. Fase 4 implementada: contexto limitado. Fase 5 implementada y validada: memoria explícita. Memoria semántica prevista para fase 6, todavía pendiente.

Matiz tras recibir la checklist completa: `ROADMAP.md` es la guía de trabajo. Las fases 4 y 5 están parcialmente completadas respecto a ese alcance: faltan resúmenes y carga limitada del historial (fase 4), categorías e importancia (fase 5). La eliminación mediante `/olvidar clave` ya está implementada y validada. Fase Q planificada después de la fase 9.

## Comportamientos que deben conservarse

### Contexto

- Hasta cinco turnos anteriores completos y 12000 caracteres por defecto, definidos en `app/config.py`.
- Excluir preguntas anteriores sin respuesta y retirar primero los turnos completos más antiguos.
- Conservar sistema y pregunta actual; con cero turnos no incluir historial anterior.
- Contar también los recuerdos y su encabezado dentro del límite.
- Si la base no cabe, rechazar antes de guardar la pregunta o consultar al modelo y retirar el mensaje provisional.
- No confundir caracteres con tokens.
- El recorte del contexto no borra el historial completo de SQLite ni de `self.messages`.

### Memoria

- Guardado explícito mediante `/recordar clave=valor` en la consola; no extraer recuerdos automáticamente de conversaciones.
- Validar separador y campos no vacíos después de eliminar espacios de los extremos.
- Dividir solo por el primer `=` y actualizar el valor si la clave ya existe.
- Procesar el comando sin consulta al LLM y sin añadir un turno al historial.
- Recuperar recuerdos desde SQLite y añadirlos a una copia del mensaje de sistema, sin modificar el original.
- Actualmente se incluyen todos los recuerdos; no hay selección semántica por relevancia.
- `obtener_memoria` devuelve `None` si no hay clave; `cargar_memoria` devuelve `{}` si no hay recuerdos.
- Borrar historial no implica borrar recuerdos.
- `/olvidar clave` elimina solo ese recuerdo, informa si no existe y rechaza claves vacías tras `strip()`. No llama al LLM ni añade turnos; no borra menciones del dato en mensajes anteriores.
- Las conexiones SQLite se cierran explícitamente con `closing`; las escrituras conservan la gestión de transacciones.

## Privacidad y datos

- No leer ni exponer secretos de `.env`. Consultar `app/config.py` y `.env.example` para entender la configuración.
- No copiar credenciales a documentación, pruebas, mensajes ni commits.
- No inspeccionar ni modificar la base real de recuerdos para pruebas ordinarias; utilizar `tmp_path` y bases temporales.
- No borrar historial ni recuerdos reales sin una solicitud explícita.
- Recordar que LOCAL FIRST no significa que toda configuración sea offline: con OpenAI, el contexto y los recuerdos incluidos se envían al servicio cloud.

## Verificación y cierre

- Elegir pruebas relevantes para los cambios autorizados. Utilizar simulaciones para evitar consultas reales a proveedores cuando no sean necesarias.
- La fixture de contexto crea el agente con `__new__`; configurar explícitamente las dependencias simuladas. En particular, `cargar_memoria.return_value` debe ser un diccionario.
- Ejecutar pruebas de contexto con `python -m pytest tests/test_contexto.py -q` y de persistencia con `python -m pytest tests/test_persistencia.py -q`.
- Para comprobar el conjunto del proyecto: `python -m pytest -q`.
- Las pruebas actuales del router instancian OpenAI y pueden requerir una clave configurada, aunque no consulten al modelo. No imprimir esa clave para diagnosticar fallos.
- Última suite completa comunicada por el usuario: 22 passed. No tratar ese resultado histórico como una ejecución nueva.
- Suite completa ejecutada por el agente al cerrar `/olvidar`: 28 passed en 1,91 s, con bases temporales y sin consultas a modelos. El usuario comunicó completar la prueba manual de eliminación y persistencia tras reiniciar.
- Validaciones manuales comunicadas: Ollama sin Internet, guardar recuerdo, preguntar el nombre, reiniciar y recuperar el dato, y rechazo de `/recordar` sin argumentos.
- Comprobar el diff y el formato de los documentos editados. No repetir pruebas de código por cambios únicamente documentales salvo que haya un motivo concreto.
- No hacer commits, push ni publicar cambios por iniciativa propia en este flujo de tutoría; esperar una petición del usuario.
