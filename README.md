# Asistente Personal IA

Asistente personal de IA en Python, modular y orientado a ejecución local. El proyecto se desarrolla progresivamente como ejercicio de aprendizaje.

> LOCAL FIRST — CLOUD WHEN NEEDED

Se priorizan soluciones locales, privadas y de bajo coste. Los servicios cloud se utilizan cuando aportan una ventaja clara.

## Estado del proyecto

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

### Alcance y privacidad

- No hay extracción automática de recuerdos, búsqueda semántica ni selección de recuerdos por relevancia.
- Todavía no existen comandos de consola para listar o eliminar recuerdos.
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

Las pruebas cubren persistencia, actualización y recuperación de recuerdos, selección de proveedores, recorte de contexto, rechazo sin efectos de guardado, incorporación de memoria y validación básica de recuerdos. Usan bases temporales, `monkeypatch` y `Mock` según el caso.

Las pruebas del router instancian proveedores; la de OpenAI necesita una clave configurada para construir el cliente, aunque no realiza una consulta al modelo.

Validaciones manuales realizadas: Ollama sin Internet, uso de `/recordar`, consulta del nombre, recuperación tras reiniciar y manejo de una orden sin argumentos. El flujo completo de consola se ha validado manualmente; no todos sus casos tienen pruebas automáticas.

## Próximos objetivos

La memoria semántica corresponde a la fase 6. A más largo plazo se prevén selección automática de proveedores, herramientas, consultas externas, automatizaciones, integraciones, voz e interfaz gráfica. Son objetivos futuros, no funcionalidades actuales.
