### LangGraph Deep Research — Scoping

Sistema mínimo de "deep research" centrado en la fase de scoping usando LangGraph + LangChain. Este módulo:

- **Detecta si falta aclaración** en la solicitud del usuario.
- **Genera un research brief** estructurado a partir del historial de mensajes.
- Muestra salidas formateadas con `rich` y puede **exportar el grafo** del flujo en formato imagen.

---

### Arquitectura en 2 nodos

1. **clarify_with_user**: decide, con salida tipada, si hay que pedir una aclaración al usuario.
2. **write_research_brief**: transforma el historial en un brief de investigación claro y accionable.

Ambos nodos se orquestan con `StateGraph` (LangGraph) y usan **salida estructurada** (Pydantic) para evitar alucinaciones.

---

### Estructura principal

- `src/langgraph_deepresearch.py`: entry point de ejemplo que compila e invoca el grafo de scoping.
- `src/research_agent_scope.py`: construcción del grafo y definición de nodos (`clarify_with_user`, `write_research_brief`).
- `src/scope/scope_state.py`: estado del agente y esquemas Pydantic (`ClarifyWithUser`, `ResearchQuestion`).
- `src/prompts/prompts.py`: plantillas de prompts para aclaración y brief.
- `src/message_utils/message_utils.py`: utilidades de salida con `rich`.
- `src/LLM_models/LLM_models.py`: selección del modelo LLM (por defecto `openai:gpt-4.1`).
- `src/debug.py`: flags para imprimir/guardar el grafo (`PRINT_SCOPE_GRAPH`, `SAVE_SCOPE_GRAPH`).

---

### Requisitos

- **Python >= 3.12**
- Dependencias (declaradas en `pyproject.toml`):
  - `langgraph`, `langchain`, `langchain-openai`, `rich`, `grandalf`, `dotenv`, `ipykernel`
- Cuenta y API Key de OpenAI (o proveedor compatible con `langchain-openai`).

---

### Instalación

Recomendado con `uv` (usa `pyproject.toml` y crea `.venv` automáticamente):

```bash
# Desde la raíz del proyecto
uv sync
source .venv/bin/activate
```

Alternativa con `pip` (instalación directa de dependencias):

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install dotenv grandalf ipykernel langchain langchain-openai langgraph rich
```

---

### Configuración

Define tu API Key en `.env` (cargada por `dotenv`):

```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

Selecciona el modelo en `src/LLM_models/LLM_models.py` si lo deseas:

```python
SCOPE_MODEL = "openai:gpt-4.1"  # opciones: openai:gpt-5, openai:gpt-5-mini, etc.
```

Controla el volcado del grafo en `src/debug.py`:

```python
PRINT_SCOPE_GRAPH = False
SAVE_SCOPE_GRAPH = True  # genera scope_graph_xray.png
```

---

### Ejecución rápida

Desde la raíz del repo (asegúrate de activar el entorno):

```bash
python src/langgraph_deepresearch.py
```

Qué hace el script de ejemplo:
- Compila el grafo con `InMemorySaver`.
- Invoca dos mensajes de usuario de ejemplo (sobre cafeterías en Madrid).
- Imprime los mensajes y el **Research Brief** formateados.
- Si `SAVE_SCOPE_GRAPH=True`, guarda una imagen del grafo (`scope_graph_xray.png`).

Nota: la ruta de salida de la imagen depende del directorio desde el que ejecutes el script.

---

### Uso programático

Puedes invocar el grafo desde tu propio código:

```python
from langgraph.checkpoint.memory import InMemorySaver
from research_agent_scope import deep_researcher_graph_builder
from langchain_core.messages import HumanMessage

checkpointer = InMemorySaver()
scope_graph = deep_researcher_graph_builder.compile(checkpointer=checkpointer)

thread = {"configurable": {"thread_id": "1"}}
result = scope_graph.invoke({
    "messages": [HumanMessage(content="Formula tu petición aquí")]
}, config=thread)

brief_or_question = result.get("research_brief")
messages = result.get("messages")
```

---

### Notebooks

- `src/langgraph_deepresearch.ipynb`: recorrido interactivo del flujo.
- `material/notebooks/1_scoping.ipynb`: material de apoyo sobre scoping.

---

### Solución de problemas

- **Model not found / API errors**: verifica `OPENAI_API_KEY` y el nombre de modelo en `SCOPE_MODEL`.
- **No se genera la imagen del grafo**: confirma `SAVE_SCOPE_GRAPH=True` y permisos de escritura en el cwd.
- **Dependencias**: si no usas `uv`, instala las versiones mínimas indicadas arriba.

---

### Licencia

Este proyecto está bajo la licencia indicada en `LICENSE`.


