# Asistente Personal IA

Proyecto personal para desarrollar un asistente de inteligencia artificial modular, escalable y orientado a ejecución local.

La filosofía principal del proyecto es:

> LOCAL FIRST — CLOUD WHEN NEEDED

Siempre que sea posible se priorizarán soluciones locales, privadas y de bajo coste. Los servicios cloud se utilizarán cuando aporten una ventaja clara en calidad o funcionalidad.

---

## Estado actual

El proyecto se encuentra actualmente en una fase inicial de arquitectura.

Funcionalidades implementadas:

- Interfaz por consola.
- Integración con OpenAI.
- Uso de GPT-5-nano.
- Historial persistente mediante SQLite.
- Recuperación automática del historial.
- Configuración mediante variables de entorno.
- Arquitectura modular básica.
- Separación entre agente, configuración y persistencia.

---

## Arquitectura actual

```text
AgenteIA/
│
├── main.py
├── README.md
├── AGENTS.md
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── agente.py
│   ├── config.py
│   │
│   └── persistence/
│       ├── __init__.py
│       └── persistencia.py
│
├── data/
│   └── memoria.db
│
├── docs/
├── logs/
└── tests/