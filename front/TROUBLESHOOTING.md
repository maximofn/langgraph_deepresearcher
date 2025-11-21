# Solución de Problemas - Interfaz Gradio

## Cambios Realizados

### 1. Interceptor de Mensajes
- **Problema**: Los eventos no se capturaban correctamente
- **Solución**: Añadido logging detallado con `[INTERCEPTOR]` prefix
- **Verificación**: Busca líneas como `[INTERCEPTOR] ✓ Event emitted: scope_start` en la consola

### 2. Estructura del Chat
- **Problema**: Mensajes del usuario se duplicaban o se unían con respuestas
- **Solución**:
  - Añadido mensaje inicial "⏳ _Procesando..._" mientras se genera respuesta
  - Eliminado yield de user_message en el wrapper
  - Respuestas separadas con `---` para claridad
- **Verificación**: El mensaje del usuario debe aparecer solo una vez en su propia burbuja

### 3. Captura de Eventos en Tiempo Real
- **Problema**: Eventos no se mostraban a tiempo
- **Solución**:
  - Aumentado intervalo de polling de 0.1s a 0.3s
  - Añadido delay de 1.0s después de completar para capturar eventos finales
- **Verificación**: Deberías ver cada paso del proceso aparecer en tiempo real

## Cómo Verificar que Funciona

### 1. Iniciar con Logging
```bash
python run_gradio.py 2>&1 | grep -E "\[INTERCEPTOR\]|Scope|Supervisor|Research|Writer"
```

Deberías ver salidas como:
```
✓ Message interception enabled
[INTERCEPTOR] ✓ Event emitted: scope_start - Scope Assistant
[INTERCEPTOR] ✓ Event emitted: scope_brief - Scope Assistant - Research brief generated
[INTERCEPTOR] ✓ Event emitted: supervisor_start - Supervisor Agent
```

### 2. Verificar en el Chat

Cuando envíes un mensaje, deberías ver:

1. **Tu mensaje** (una sola vez, arriba)
2. **Indicador de procesamiento**: "⏳ _Procesando..._"
3. **Eventos del Scope Agent** (🔵):
   ```
   🔵 **Scope Assistant - need clarification?**
   _Contenido en itálica (intermedio)_

   ---

   🔵 **Scope Assistant - Research brief generated**
   _Research Brief: ..._
   ```
4. **Eventos del Supervisor** (🟣):
   ```
   🟣 **Supervisor Agent**
   _Coordinando investigación..._
   ```
5. **Eventos de Research** (🟢):
   ```
   🟢 **Research Agent - Tool Call**
   _Llamando a herramienta..._
   ```
6. **Writer Agent** (🟠):
   ```
   🟠 **Writer Agent**
   _Generando informe final..._
   ```
7. **Informe Final** (sin itálica):
   ```
   **📋 Informe Final**

   [Contenido del informe en markdown]
   ```

### 3. Verificar Separadores

Entre cada sección debería aparecer `---` para separar visualmente los eventos.

## Problemas Comunes y Soluciones

### No se muestran eventos intermedios

**Diagnóstico**:
```bash
# En la terminal donde ejecutas run_gradio.py
# Busca líneas de [INTERCEPTOR]
```

**Posibles causas**:
1. El interceptor no se habilitó correctamente
   - **Solución**: Verifica que veas "✓ Message interception enabled" al inicio
2. Los eventos se emiten pero no se yielden a tiempo
   - **Solución**: Ya aumentamos el delay a 0.3s y 1.0s final

### Mensajes duplicados

**Diagnóstico**: Verifica que en `gradio_app.py` línea 96-97 se esté filtrando `user_message`:
```python
if event.get("type") == "user_message":
    continue
```

### Eventos se pierden

**Diagnóstico**: Verifica en consola si se emiten pero no se muestran:
```bash
# Terminal 1: Ejecutar Gradio
python run_gradio.py

# Terminal 2: Ver solo eventos interceptados
tail -f /dev/stdout | grep "\[INTERCEPTOR\]"
```

**Si ves eventos en consola pero no en UI**:
- El problema está en el polling del wrapper
- Aumenta el delay final de 1.0s a 2.0s en `deep_researcher_wrapper.py` línea 84 y 170

### Clarificaciones no funcionan

**Diagnóstico**: Verifica que `self.waiting_for_clarification` se esté configurando correctamente en `gradio_app.py` línea 104-105.

**Solución**: Asegúrate de que el evento de tipo "clarification" se detecte correctamente.

## Depuración Avanzada

### Ver todos los eventos capturados

Añade esto temporalmente en `deep_researcher_wrapper.py` antes de yielding:
```python
# Después de la línea 91
print(f"[DEBUG] Total events captured: {len(all_events)}")
print(f"[DEBUG] New events to yield: {len(new_events)}")
for event in new_events:
    print(f"[DEBUG] Event: {event.event_type.value} - {event.title}")
```

### Ver estado del tracker

Añade en `gradio_app.py` en el método `process_message`:
```python
# Después de yield history (línea 109)
print(f"[DEBUG UI] Response parts count: {len(response_parts)}")
```

## Mejoras Futuras

Si los eventos aún no se capturan bien, considera:

1. **Usar callbacks síncronos** en lugar de polling:
   ```python
   def event_callback(event):
       # Guardar en una cola thread-safe
       event_queue.put(event)
   ```

2. **Usar websockets** para comunicación en tiempo real

3. **Capturar stdout directamente** con un custom handler:
   ```python
   import sys
   from io import StringIO

   old_stdout = sys.stdout
   sys.stdout = custom_handler
   ```

## Contacto y Soporte

Si sigues teniendo problemas:
1. Verifica que todas las dependencias estén instaladas: `uv sync`
2. Revisa que las variables de entorno estén configuradas
3. Prueba con un modelo más simple primero para aislar el problema
4. Comparte los logs completos de la consola
