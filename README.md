# Asistente Personal IA

Asistente personal de IA en Python, modular y orientado a ejecución local. El proyecto se desarrolla progresivamente como ejercicio de aprendizaje.

> LOCAL FIRST — CLOUD WHEN NEEDED

Se priorizan soluciones locales, privadas y de bajo coste. Los servicios cloud se utilizan cuando aportan una ventaja clara.

## Estado del proyecto

La checklist completa se mantiene en [ROADMAP.md](ROADMAP.md). Según su alcance ampliado, las fases 4 y 5 están parcialmente completadas: funcionan el contexto limitado y la memoria explícita con eliminación, pero faltan resúmenes, carga limitada del historial, categorías e importancia.

- Fases 1 y 2: base del asistente, consola, configuración, integración con OpenAI e historial persistente.
- Fase 3: proveedores separados y ejecución local con Ollama. Validado manualmente con `qwen3:4b` sin Internet.
- Fase 4: selección del contexto por turnos completos y límite de caracteres.
- Fase 5: memoria explícita clave-valor en SQLite, actualización, recuperación e integración en el contexto mediante `/recordar`.
- Fase 6 prevista: memoria semántica; todavía no implementada.

El proveedor se elige mediante configuración. Aún no hay selección inteligente ni cambio automático de proveedor ante fallos.

## Estructura y responsabilidades

```text
AgenteIA/
├── main.py                         # Entrada de la aplicación
├── AGENTS.md                       # Reglas para colaborar en el proyecto
├── README.md
├── requirements.txt
├── pytest.ini
├── .env.example
├── .env                            # Configuración local; no publicar
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── agente.py                   # Conversación, contexto y comandos
│   ├── config.py                   # Configuración y rutas
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py                 # Interfaz común de proveedores
│   │   ├── router.py               # Selección por LLM_PROVIDER
│   │   ├── ollama_provider.py      # Modelo local
│   │   └── openai_provider.py      # API Responses de OpenAI
│   └── persistence/
│       ├── __init__.py
│       └── persistencia.py         # Acceso a SQLite
├── data/
│   └── memoria.db                 # Historial y recuerdos locales
├── docs/
├── logs/
└── tests/
    ├── test_persistencia.py
    ├── test_llm_router.py
    └── test_contexto.py
```

`env/` es el entorno virtual local, si se crea con ese nombre. Las carpetas de datos, documentación y logs se crean cuando se inicializa la persistencia por defecto; su existencia no implica que ya haya un sistema de logging implementado.

## Preparación y ejecución en Windows

Desde la carpeta del proyecto, con Python disponible:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Crea `.env` tomando `.env.example` como referencia si aún no existe. No sobrescribas una configuración existente. El ejemplo actual contiene los campos de OpenAI y el nombre del asistente; puedes añadir los de Ollama y del proveedor.

### Configuración

| Variable | Valor por defecto en el código | Uso |
| --- | --- | --- |
| `LLM_PROVIDER` | `ollama` | `ollama` u `openai` |
| `OLLAMA_MODEL` | `qwen3:4b` | Modelo que utiliza Ollama |
| `OPENAI_MODEL` | `gpt-5-nano` | Modelo que utiliza OpenAI |
| `OPENAI_API_KEY` | Sin valor | Credencial necesaria para OpenAI |
| `ASSISTANT_NAME` | `Asistente` | Nombre mostrado por el asistente |

Para trabajar localmente, instala y ejecuta Ollama y descarga el modelo antes de trabajar sin conexión:

```powershell
ollama pull qwen3:4b
```

Configura en `.env`:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:4b
ASSISTANT_NAME=Asistente
```

Para OpenAI, usa `LLM_PROVIDER=openai` y configura tu clave y modelo. Esta opción necesita acceso al servicio y puede tener coste. No publiques la clave ni el archivo `.env`.

Inicia el asistente:

```powershell
python main.py
```

Escribe preguntas en la consola. Para terminar puedes usar `salir`, `exit`, `adios` o `agur`. Las entradas vacías se ignoran.

## Historial y contexto — Fase 4

SQLite guarda los mensajes y los carga al iniciar. `self.messages` también conserva el historial completo en memoria durante la sesión. El recorte afecta solo al contexto enviado al modelo, no borra mensajes guardados.

Los límites actuales están definidos en `app/config.py`, no como variables de entorno:

- `MAX_CONTEXT_TURNS = 5`: hasta cinco turnos anteriores completos, cada uno formado por pregunta y respuesta.
- `MAX_CONTEXT_CHARS = 12000`: máximo de caracteres del contenido de los mensajes enviados.

El contexto conserva el mensaje de sistema y la pregunta actual. Excluye preguntas anteriores sin respuesta y retira los turnos completos más antiguos cuando no caben. Con cero turnos permitidos, no incorpora historial anterior.

El sistema, la memoria y la pregunta actual forman la base del contexto. Si esa base supera el límite, se lanza un error, se retira la pregunta provisional de `self.messages` y no se guarda la pregunta ni se consulta al modelo. El límite mide caracteres, no tokens.

## Memoria explícita — Fase 5

Los recuerdos se guardan en la tabla `memoria` de la misma base SQLite, separados de la tabla `mensajes`. Cada recuerdo tiene una `clave` única y un `valor` de texto.

En la consola del asistente:

```text
/recordar usuario=Carlos
```

El programa confirma `Recordado: usuario = Carlos`. Repite la clave para actualizar el valor:

```text
/recordar usuario=Luis
```

La orden elimina espacios de los extremos de ambos campos. Requiere `=` y una clave y un valor no vacíos. Solo divide por el primer `=`, por lo que el valor puede contener otros signos iguales. Un formato inválido muestra un error y permite seguir usando la consola.

El comando guarda directamente en SQLite, sin consultar al modelo ni añadir un turno de conversación. Conversar por sí solo no crea recuerdos: el guardado es explícito.

En cada consulta se recuperan todos los recuerdos y se añaden a una copia del mensaje de sistema, identificados como datos. El mensaje de sistema original permanece intacto. Los recuerdos y su encabezado cuentan dentro del límite de caracteres.

Puedes preguntar `¿Cómo me llamo?` después de guardar el nombre y también tras reiniciar. Esta recuperación no depende de que el turno original siga entre los cinco recientes.

### Eliminar un recuerdo

Usa `/olvidar clave`, por ejemplo `/olvidar usuario`. Se eliminan los espacios de los extremos de la clave y se muestra `Olvidado: usuario` si existía, o `No existe el recuerdo: usuario` si no existía. Una clave vacía muestra `Error: Usa /olvidar clave` y permite continuar.

La eliminación es persistente y afecta solo al recuerdo seleccionado. No consulta al modelo ni añade mensajes al historial. Tampoco borra menciones anteriores de ese dato en el historial de conversación; esas menciones todavía pueden formar parte de los turnos recientes enviados al modelo.

Todas las operaciones de persistencia cierran explícitamente sus conexiones SQLite mediante `closing`. Las escrituras conservan la gestión de transacciones para confirmar los cambios o revertirlos ante errores.

### Alcance y privacidad

- No hay extracción automática de recuerdos, búsqueda semántica ni selección de recuerdos por relevancia.
- Todavía no existe un comando de consola para listar recuerdos.
- `borrar_historial()` elimina mensajes; no elimina la tabla de recuerdos.
- Una memoria demasiado grande puede impedir consultas hasta reducir sus valores; no se trunca automáticamente.
- Los recuerdos se almacenan localmente, pero se envían al proveedor configurado cuando forman parte del contexto. Con OpenAI, salen del equipo junto con ese contexto.

## Pruebas y validación

Con el entorno virtual activado:

```powershell
python -m pytest -q
```

También puedes ejecutar por archivo:

```powershell
python -m pytest tests/test_persistencia.py -q
python -m pytest tests/test_contexto.py -q
python -m pytest tests/test_llm_router.py -q
```

Último resultado de la suite completa comunicado por el usuario: **22 passed**. Es un resultado de validación, no un número fijo que deban conservar futuras versiones.

Última suite completa ejecutada por el agente al cerrar el bloque de `/olvidar`: **28 passed en 1,91 s**, con bases temporales, dependencias simuladas y sin consultas a modelos. Se utilizó una clave ficticia solo para construir el cliente OpenAI en las pruebas del router.

Las pruebas de eliminación cubren el borrado selectivo, una clave inexistente, la limpieza de espacios, el rechazo de claves vacías y la conexión del comando de consola sin llamadas al LLM ni cambios en el historial. El usuario también comunicó haber completado la comprobación manual de `/olvidar`, incluyendo la repetición tras reiniciar.

Las pruebas cubren persistencia, actualización y recuperación de recuerdos, selección de proveedores, recorte de contexto, rechazo sin efectos de guardado, incorporación de memoria y validación básica de recuerdos. Usan bases temporales, `monkeypatch` y `Mock` según el caso.

Las pruebas del router instancian proveedores; la de OpenAI necesita una clave configurada para construir el cliente, aunque no realiza una consulta al modelo.

Validaciones manuales realizadas: Ollama sin Internet, uso de `/recordar`, consulta del nombre, recuperación tras reiniciar y manejo de una orden sin argumentos. El flujo completo de consola se ha validado manualmente; no todos sus casos tienen pruebas automáticas.

## Próximos objetivos

La memoria semántica corresponde a la fase 6. A más largo plazo se prevén selección automática de proveedores, herramientas, consultas externas, automatizaciones, integraciones, voz e interfaz gráfica. Son objetivos futuros, no funcionalidades actuales.

### Fase Q — Formación en computación cuántica y optimización híbrida

Planificada como una pausa temporal del desarrollo funcional: **Fase 9 — Router inteligente de modelos → Fase Q → continuación del roadmap**. Todas las tareas siguientes están pendientes. Esta sección registra la nueva fase; no sustituye la checklist completa del proyecto.

- [ ] Estudiar con recursos oficiales, principalmente IBM Quantum y Qiskit: funciones objetivo, restricciones, variables binarias, QUBO, Ising, algoritmos variacionales y QAOA.
- [ ] Practicar simulación, ruido, transpilación y workflows híbridos; utilizar hardware cuántico cuando sea razonable.
- [ ] **Q1 — Fundamentos con QAOA:** formular Max-Cut, resolverlo clásicamente, convertirlo a QUBO/Ising, ejecutar QAOA en simulador y comparar resultados.
- [ ] **Q2 — Routing de modelos IA:** asignar tareas a Python, modelos locales pequeños/grandes o API externa, considerando coste, latencia, RAM, VRAM, calidad estimada y privacidad. Crear formulación matemática, baseline clásico, QUBO y comparativa con QAOA.
- [ ] **Q3 — Recursos hardware:** formular un scheduler de trabajos para CPU, GPU y cloud con prioridad, duración, memoria, plazo y coste. Comparar soluciones clásicas e híbridas según tiempo total, coste, prioridades y uso de recursos.
- [ ] **Q4 — Proyecto de portfolio:** ampliar Q2 o Q3 con warm-start QAOA, distintos optimizadores y profundidades, análisis de ruido, transpilación, hardware real y benchmarking.
- [ ] Preparar cada mini-proyecto como repositorio independiente con `README.md`, `src/`, `notebooks/`, `tests/`, `results/` y `requirements.txt`.
- [ ] Documentar en cada proyecto el problema, formulación, soluciones clásica y cuántica, instancias, metodología, métricas, resultados, gráficas, limitaciones, conclusiones e instrucciones reproducibles.

Los experimentos deben partir de problemas reales de optimización. No se afirmará una ventaja cuántica sin evidencia experimental. La fase persigue aprendizaje y proyectos demostrables; no implica incorporar computación cuántica al asistente.
