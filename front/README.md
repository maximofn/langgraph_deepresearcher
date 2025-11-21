# Deep Researcher - Interfaz Gradio

Interfaz web moderna para el sistema Deep Researcher, con visualización en tiempo real de todos los componentes del sistema multi-agente.

## Características

- **Interfaz de Chat**: Interacción natural con el sistema de investigación
- **Salidas Transparentes**: Las salidas intermedias se muestran con transparencia (como los modelos de razonamiento modernos)
- **Diferenciación Visual**: Cada componente tiene su propio estilo visual:
  - 🔵 **Scope Agent**: Azul - Análisis y clarificación
  - 🟣 **Supervisor Agent**: Morado - Coordinación de investigación
  - 🟢 **Research Agents**: Verde - Ejecución de investigaciones
  - 🟠 **Writer Agent**: Naranja - Generación del informe final
- **Informe Final en Markdown**: El informe final se renderiza con formato completo

## Instalación

Las dependencias necesarias ya están incluidas en el `pyproject.toml` del proyecto:

```bash
# Asegúrate de tener el entorno virtual activado
source .venv/bin/activate

# Instala las dependencias (si aún no lo has hecho)
uv sync
```

## Uso

### Iniciar la Interfaz

```bash
# Desde el directorio raíz del proyecto
python front/gradio_app.py
```

O usando uv:

```bash
uv run python front/gradio_app.py
```

La interfaz estará disponible en: `http://localhost:7860`

### Flujo de Uso

1. **Introduce tu pregunta**: Escribe sobre qué quieres investigar
2. **Observa el proceso**: Verás las salidas de cada componente en tiempo real:
   - El Scope Agent verificará si necesita clarificación
   - Si es necesario, te pedirá más información
   - El Supervisor coordina la investigación
   - Los Research Agents trabajan en paralelo
   - El Writer genera el informe final
3. **Recibe el informe**: El informe final se muestra con formato completo

### Ejemplo de Uso

```
Usuario: "Quiero investigar las mejores cafeterías de Madrid."

[Scope Agent verifica clarificación - transparente]
[Scope Agent genera research brief - transparente]
[Supervisor delega investigaciones - transparente]
[Research Agents investigan en paralelo - transparente]
[Writer Agent genera informe - transparente]
[Informe Final - destacado sin transparencia]
```

## Arquitectura

### Componentes Principales

1. **`event_tracker.py`**: Sistema de eventos para capturar salidas
   - `EventTracker`: Clase principal para gestión de eventos
   - `EventType`: Enum con tipos de eventos
   - `Event`: Dataclass para representar eventos

2. **`deep_researcher_wrapper.py`**: Wrapper del sistema Deep Researcher
   - `DeepResearcherWrapper`: Envuelve el sistema y emite eventos
   - Captura salidas de consola
   - Gestiona el flujo de investigación

3. **`gradio_app.py`**: Interfaz Gradio
   - `DeepResearcherUI`: Clase principal de la UI
   - Estilos CSS personalizados
   - Manejo de eventos de chat

### Flujo de Eventos

```
Usuario → Gradio UI → DeepResearcherWrapper → Deep Researcher
                ↓
         Event Tracker
                ↓
         Gradio UI (actualización en tiempo real)
```

## Personalización

### Modificar Estilos

Los estilos CSS están definidos en `CUSTOM_CSS` dentro de `gradio_app.py`. Puedes modificar:

- Colores de cada componente
- Transparencia de salidas intermedias
- Estilos de texto y márgenes
- Efectos visuales

### Añadir Nuevos Tipos de Eventos

1. Añade el nuevo tipo en `EventType` (event_tracker.py)
2. Emite el evento en `DeepResearcherWrapper._parse_and_emit_events()`
3. Añade el formato HTML en `DeepResearcherUI._format_event()`

### Configurar el Servidor

Modifica los parámetros en `app.launch()`:

```python
app.launch(
    server_name="0.0.0.0",  # Acceso desde cualquier IP
    server_port=7860,        # Puerto del servidor
    share=False             # True para crear link público
)
```

## Solución de Problemas

### El servidor no inicia

- Verifica que el puerto 7860 esté disponible
- Comprueba que todas las dependencias estén instaladas
- Verifica que las variables de entorno (API keys) estén configuradas

### No se muestran las salidas intermedias

- Verifica que el `event_tracker` esté funcionando
- Comprueba los logs de consola para errores
- Asegúrate de que el wrapper esté capturando correctamente las salidas

### Errores de importación

- Verifica que `sys.path.append('src')` esté correctamente configurado
- Asegúrate de ejecutar desde el directorio raíz del proyecto
- Comprueba que todos los módulos del proyecto estén accesibles

## Próximas Mejoras

- [ ] Mostrar progreso de cada research agent individualmente
- [ ] Añadir botón para exportar el informe final
- [ ] Implementar historial de investigaciones
- [ ] Añadir visualización de grafos del flujo de agentes
- [ ] Soporte para múltiples sesiones simultáneas
- [ ] Métricas de rendimiento en tiempo real

## Notas Técnicas

- La interfaz usa `asyncio` para operaciones asíncronas
- Los eventos se capturan mediante callbacks
- La salida de consola se redirige temporalmente para capturar logs
- El estado de la conversación se mantiene en el checkpointer
