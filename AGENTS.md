# AGENTS.md

## 1. Objetivo del proyecto

Este proyecto tiene como objetivo construir un asistente personal de IA local, modular y escalable.

El asistente debe evolucionar progresivamente hasta poder:

- Mantener memoria persistente.
- Utilizar modelos de IA locales y en la nube.
- Elegir automáticamente entre distintos proveedores de IA.
- Ejecutar herramientas.
- Consultar información externa.
- Automatizar tareas.
- Integrarse con servicios externos.
- Incorporar voz e interfaces gráficas.
- Funcionar parcialmente o completamente sin conexión a Internet cuando sea posible.

La filosofía general del proyecto es:

> LOCAL FIRST — CLOUD WHEN NEEDED

Siempre que sea razonable, se priorizarán soluciones locales, gratuitas y privadas.

Los servicios cloud se utilizarán cuando aporten una ventaja clara en calidad, capacidad o funcionalidad.


---

# 2. Principios generales

Todo cambio realizado en el proyecto debe respetar los siguientes principios:

1. Mantener el código simple y legible.
2. Separar responsabilidades entre módulos.
3. Evitar archivos excesivamente grandes.
4. Evitar dependencias innecesarias.
5. Evitar duplicación de código.
6. Mantener compatibilidad con funcionalidades existentes.
7. No introducir complejidad antes de que sea necesaria.
8. Priorizar soluciones fácilmente mantenibles.
9. Preparar el proyecto para crecer progresivamente.
10. Mantener la privacidad de los datos del usuario.


---

# 3. Arquitectura actual

La estructura actual del proyecto es:

```text
AgenteIA/
│
├── main.py
├── AGENTS.md
├── README.md
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