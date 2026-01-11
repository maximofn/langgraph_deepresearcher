# Deep Researcher API

API REST con WebSocket para el sistema de investigación multi-agente LangGraph Deep Researcher.

## Características

- **WebSocket Streaming**: Eventos en tiempo real durante la investigación
- **Multi-usuario**: Múltiples sesiones concurrentes aisladas
- **Persistencia**: Base de datos SQLite (fácil migración a PostgreSQL)
- **Async**: Totalmente asíncrono con FastAPI y LangGraph
- **Eventos detallados**: Seguimiento de todo el proceso de investigación (Scope → Supervisor → Research → Writer)

## Instalación

### 1. Instalar Dependencias

```bash
uv sync
```

### 2. Configurar Variables de Entorno

Copiar el archivo de ejemplo y editarlo con tus API keys:

```bash
cp .env.example .env
```

Editar `.env` y configurar:

```bash
# API Keys (REQUERIDAS)
OPENAI_API_KEY=tu_clave_openai
ANTHROPIC_API_KEY=tu_clave_anthropic
TAVILY_API_KEY=tu_clave_tavily

# API Configuration (OPCIONAL)
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

### 3. Iniciar la API

```bash
uv run python run_api.py
```

O directamente con uvicorn:

```bash
uv run uvicorn api.main:app --reload
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI interactivo)
- **WebSocket**: ws://localhost:8000/ws/{session_id}

## Uso

### Flujo Básico

#### 1. Crear una Sesión

```bash
curl -X POST http://localhost:8000/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuáles son los mejores cafés en Madrid?",
    "max_iterations": 6,
    "max_concurrent_researchers": 3
  }'
```

Respuesta:

```json
{
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "thread_id": "660e8400-e29b-41d4-a716-446655440001",
    "status": "created",
    "initial_query": "¿Cuáles son los mejores cafés en Madrid?",
    "created_at": "2026-01-10T12:00:00Z",
    ...
  },
  "websocket_url": "/ws/550e8400-e29b-41d4-a716-446655440000"
}
```

#### 2. Conectar WebSocket (en JavaScript)

```javascript
const sessionId = "550e8400-e29b-41d4-a716-446655440000";
const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  if (message.type === "event") {
    const { event_type, title, content, is_intermediate } = message.data;

    console.log(`[${event_type}] ${title}`);

    if (event_type === "CLARIFICATION_NEEDED") {
      // Mostrar formulario de clarificación
      showClarificationForm(content);
    } else if (event_type === "FINAL_REPORT") {
      // Mostrar reporte final
      displayReport(content);
    } else if (is_intermediate) {
      // Mostrar progreso intermedio
      appendLog(title, content);
    }
  }
};

ws.onopen = () => console.log("WebSocket conectado");
ws.onerror = (error) => console.error("Error WebSocket:", error);
```

#### 3. Iniciar Investigación

```bash
curl -X POST http://localhost:8000/sessions/550e8400-e29b-41d4-a716-446655440000/start
```

Respuesta:

```json
{
  "status": "started",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Research started. Connect to WebSocket for real-time updates."
}
```

#### 4. (Si necesario) Proveer Clarificación

Si el evento `CLARIFICATION_NEEDED` es recibido:

```bash
curl -X POST http://localhost:8000/sessions/550e8400-e29b-41d4-a716-446655440000/clarify \
  -H "Content-Type: application/json" \
  -d '{"clarification": "Enfócate en la calidad del café"}'
```

#### 5. Obtener Resultados

Una vez completada la investigación (evento `FINAL_REPORT`):

```bash
curl http://localhost:8000/sessions/550e8400-e29b-41d4-a716-446655440000
```

## API Endpoints

### REST Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/sessions/` | Crear nueva sesión |
| `POST` | `/sessions/{id}/start` | Iniciar investigación |
| `POST` | `/sessions/{id}/clarify` | Proveer clarificación |
| `GET` | `/sessions/{id}` | Obtener detalles de sesión |
| `GET` | `/sessions/{id}/messages` | Obtener mensajes de sesión |
| `GET` | `/sessions/` | Listar todas las sesiones |
| `GET` | `/health` | Health check |

### WebSocket

| Endpoint | Descripción |
|----------|-------------|
| `ws://localhost:8000/ws/{session_id}` | Stream de eventos en tiempo real |

## Tipos de Eventos WebSocket

Eventos emitidos durante la investigación:

### Eventos de Sesión
- `SESSION_CREATED`: Sesión creada
- `SESSION_STARTED`: Investigación iniciada

### Eventos de Scope Agent
- `SCOPE_START`: Análisis inicial
- `SCOPE_CLARIFICATION`: Necesita clarificación
- `SCOPE_BRIEF`: Research brief generado

### Eventos de Supervisor Agent
- `SUPERVISOR_START`: Supervisor inicia
- `SUPERVISOR_THINKING`: Planificación estratégica
- `SUPERVISOR_DELEGATION`: Delegación a research agents

### Eventos de Research Agents
- `RESEARCH_START`: Research agent inicia
- `RESEARCH_TOOL_CALL`: Búsqueda web ejecutándose
- `RESEARCH_TOOL_OUTPUT`: Resultados de búsqueda
- `RESEARCH_COMPLETE`: Research completado
- `COMPRESSION`: Síntesis de findings

### Eventos de Writer Agent
- `WRITER_START`: Generación de reporte
- `WRITER_COMPLETE`: Writer completado

### Eventos Finales
- `FINAL_REPORT`: Reporte final generado
- `CLARIFICATION_NEEDED`: Necesita input del usuario
- `ERROR`: Error durante investigación

## Formato de Mensajes WebSocket

```json
{
  "type": "event",
  "data": {
    "event_type": "SUPERVISOR_THINKING",
    "title": "Supervisor Planning",
    "content": "Analyzing research requirements...",
    "is_intermediate": true,
    "timestamp": 1704902400.123,
    "metadata": {}
  }
}
```

Tipos de mensaje:
- `"connected"`: Conexión establecida
- `"event"`: Evento de investigación
- `"ping"`: Keep-alive
- `"error"`: Error

## Estructura del Proyecto

```
api/
├── main.py                    # Aplicación FastAPI
├── config.py                  # Configuración
├── models/
│   ├── events.py              # Modelos de eventos
│   ├── requests.py            # Request models
│   └── responses.py           # Response models
├── database/
│   ├── db.py                  # DB session
│   ├── models.py              # SQLAlchemy models
│   └── checkpointer.py        # LangGraph checkpointer
├── services/
│   ├── event_service.py       # Event tracking
│   ├── session_service.py     # Session CRUD
│   └── research_service.py    # Research execution
├── websockets/
│   ├── connection_manager.py  # WebSocket connections
│   └── message_interceptor.py # Event interception
└── routes/
    ├── sessions.py            # REST endpoints
    └── websocket.py           # WebSocket endpoint
```

## Configuración Avanzada

### Variables de Entorno

```bash
# API Configuration
API_HOST=0.0.0.0                    # Host (0.0.0.0 para todas las interfaces)
API_PORT=8000                        # Puerto
DEBUG=false                          # Modo debug (activa hot-reload)

# Database
DATABASE_URL=sqlite+aiosqlite:///./deepresearcher.db  # Base de datos de sesiones
CHECKPOINTS_DB=checkpoints.db                          # Base de datos de checkpoints

# Session Management
SESSION_EXPIRY_HOURS=24              # Horas antes de expirar sesiones

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000  # Orígenes permitidos
```

### Migrar a PostgreSQL

1. Instalar dependencias:

```bash
uv add asyncpg psycopg2-binary langgraph-checkpoint-postgres
```

2. Actualizar `.env`:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost/deepresearcher
```

3. Actualizar [api/database/checkpointer.py](api/database/checkpointer.py):

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

checkpointer = AsyncPostgresSaver.from_conn_string(settings.database_url)
```

## Testing

### Test Manual con curl

```bash
# 1. Crear sesión
SESSION_ID=$(curl -s -X POST http://localhost:8000/sessions/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the best Python libraries for AI?"}' \
  | jq -r '.session.id')

echo "Session ID: $SESSION_ID"

# 2. Iniciar investigación
curl -X POST http://localhost:8000/sessions/$SESSION_ID/start

# 3. Consultar estado
curl http://localhost:8000/sessions/$SESSION_ID | jq
```

### Test con WebSocket (usando wscat)

```bash
# Instalar wscat
npm install -g wscat

# Conectar
wscat -c ws://localhost:8000/ws/$SESSION_ID
```

## Cliente de Ejemplo en Python

```python
import asyncio
import aiohttp
import json

async def main():
    # Crear sesión
    async with aiohttp.ClientSession() as session:
        # 1. Crear
        async with session.post(
            "http://localhost:8000/sessions/",
            json={"query": "Best cafes in Madrid"}
        ) as resp:
            data = await resp.json()
            session_id = data["session"]["id"]
            print(f"Session: {session_id}")

        # 2. Conectar WebSocket
        async with session.ws_connect(
            f"ws://localhost:8000/ws/{session_id}"
        ) as ws:
            # 3. Iniciar investigación
            async with session.post(
                f"http://localhost:8000/sessions/{session_id}/start"
            ):
                pass

            # 4. Recibir eventos
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    event = json.loads(msg.data)
                    if event["type"] == "event":
                        data = event["data"]
                        print(f"[{data['event_type']}] {data['title']}")

                        if data["event_type"] == "FINAL_REPORT":
                            print("\n=== FINAL REPORT ===")
                            print(data["content"])
                            break

asyncio.run(main())
```

## Troubleshooting

### Error: "Database is locked"

SQLite tiene limitaciones de concurrencia. Para producción, usa PostgreSQL.

### WebSocket se desconecta

Verifica que el evento loop esté corriendo correctamente. FastAPI maneja esto automáticamente.

### Eventos no se reciben

Asegúrate de que la sesión esté iniciada (`/sessions/{id}/start`) después de conectar el WebSocket.

## Roadmap

- [ ] Autenticación con API Keys / JWT
- [ ] Rate limiting
- [ ] Métricas y monitoring
- [ ] Tests automatizados
- [ ] Cliente Python SDK
- [ ] Cliente JavaScript SDK
- [ ] Docker deployment

## Soporte

Para problemas o preguntas, ver:
- [CLAUDE.md](CLAUDE.md) - Documentación técnica completa
- [Issues](https://github.com/tu-repo/issues)
