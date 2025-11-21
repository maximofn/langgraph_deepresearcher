# 🚀 Inicio Rápido - Interfaz Gradio

## Ejecutar la Interfaz

```bash
# Opción 1: Script directo
python run_gradio.py

# Opción 2: Con uv
uv run python run_gradio.py

# Opción 3: Desde el módulo
python front/gradio_app.py
```

La interfaz estará disponible en: **http://localhost:7860**

## Uso

1. **Introduce tu pregunta de investigación** en el campo de texto
2. **Observa el proceso** en tiempo real:
   - 🔵 **Scope Agent**: Verifica si necesita clarificación
   - 🟣 **Supervisor Agent**: Coordina la investigación
   - 🟢 **Research Agents**: Ejecutan investigaciones en paralelo
   - 🟠 **Writer Agent**: Genera el informe final
3. **Recibe el informe** completo en formato markdown

## Ejemplo

```
Usuario: "Investiga las mejores prácticas de desarrollo con LangGraph"

🔵 Scope Agent - Clarification Check
   Verificando si se necesita clarificación...

🔵 Scope Agent - Research Brief
   Generando research brief...

🟣 Supervisor Agent
   Coordinando investigación...

🟢 Research Agent - Topic 1
   Investigando mejores prácticas de arquitectura...

🟢 Research Agent - Topic 2
   Investigando patrones de diseño...

🟠 Writer Agent
   Generando informe final...

📋 Informe Final
   [Informe completo en markdown]
```

## Características

- ✅ **Streaming en tiempo real**: Ve el progreso a medida que sucede
- ✅ **Salidas transparentes**: Los pasos intermedios se muestran con formato italic
- ✅ **Diferenciación visual**: Cada componente tiene su propio emoji y estilo
- ✅ **Soporte para clarificación**: Si el sistema necesita más información, te lo pedirá
- ✅ **Informe en Markdown**: El resultado final se renderiza con formato completo

## Solución de Problemas

### Puerto ocupado
Si el puerto 7860 está ocupado, modifica `server_port` en `front/gradio_app.py` o `run_gradio.py`

### Variables de entorno
Asegúrate de tener configuradas todas las API keys necesarias en tu archivo `.env`:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `TAVILY_API_KEY`
- `LANGSMITH_API_KEY`
- etc.

### Errores de importación
Ejecuta desde el directorio raíz del proyecto:
```bash
cd /path/to/langgraph_deepresearcher
python run_gradio.py
```

## Más Información

Consulta `front/README.md` para documentación completa sobre:
- Arquitectura del sistema
- Personalización de estilos
- Añadir nuevos tipos de eventos
- Configuración avanzada
