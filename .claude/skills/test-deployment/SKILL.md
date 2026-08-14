---
name: test-deployment
description: Batería de pruebas de extremo a extremo del Deep Researcher (API en Fly.io + web en Cloudflare) simulando distintos tipos de usuario. Úsala cuando se pida "prueba el sistema", "prueba el despliegue", "mira si algo falla" o similar, ya sea contra producción o contra local.
---

# Probar el Deep Researcher como si fueras usuarios reales

El objetivo no es que los endpoints devuelvan 200. Es **encontrar lo que se rompe
cuando alguien usa la aplicación de verdad**: el que se equivoca al pegar la clave,
el que baja un slider, el que recarga la página a mitad, el que pregunta algo
después de leer el informe.

Un 200 no es una prueba superada. Un informe largo tampoco. Hay que verificar que
lo que el sistema devuelve se corresponde con lo que dijo haber hecho.

## Antes de empezar

Decide contra qué entorno pruebas y dilo explícitamente en el informe final:

- **Producción**: `https://langgraph-deepresearcher.fly.dev` (WS: `wss://…`).
  Es el sistema real. Crea sesiones en la BD de producción, así que hay que limpiar.
- **Local**: `docker compose up --build -d api` → `http://localhost:8000`.
  Permite leer tracebacks al momento; imprescindible si hay que iterar sobre un fallo.

**Producción no tiene claves de LLM propias.** `fly secrets list` solo devuelve
`TAVILY_API_KEY`, `CORS_ORIGINS` y `RESEND_API_KEY`: el modelo lo paga el usuario
con su clave. Por tanto, toda sesión de prueba debe enviar `api_keys` leídas del
`.env` local, igual que haría alguien que las pega en Settings. Sin eso, cada
creación de sesión responde 422 y no pruebas nada.

Usa modelos pequeños (`gpt-4.1-mini`) para todos los roles salvo que el objetivo
sea evaluar calidad de redacción. La configuración por defecto (GPT-4.1 + Sonnet)
cuesta bastante más por sesión y no aporta nada a una prueba funcional.

## Cómo se estructura la batería

Cuatro fases, de barata a cara. Ejecuta las baratas primero: si el aislamiento
entre usuarios está roto, no hace falta gastar en investigaciones.

### Fase 1 — Sin gasto de LLM

Todo lo que no dispara el grafo. Es rápido y cubre mucha superficie:

- **El curioso**: `/health`, `/`, catálogo de modelos, listar sesiones con un
  `X-Client-ID` nuevo (debe venir vacío), pedir una sesión inexistente.
- **El torpe**: formularios mal rellenados. Query vacía, query de 6000 caracteres,
  `max_iterations` fuera de rango, rol inventado, modelo inventado, email mal
  escrito, clave de API con nombre no permitido (`TAVILY_API_KEY` está
  deliberadamente vetada), clave en blanco, y el caso más importante: **usuario
  que no ha abierto Settings y no manda ninguna clave**.
- **El intruso**: crea una sesión con el cliente A e intenta leerla, listar sus
  mensajes, arrancarla, borrarla y chatear con ella desde el cliente B. Todo debe
  responder 404 (no 403: no se filtra ni siquiera la existencia de la sesión).
- **Transiciones imposibles**: chatear antes de que termine, aclarar sin que te lo
  hayan pedido, arrancar dos veces la misma sesión. Deben dar 400.
- **WebSocket**: conectar con el `client_id` de otro, a una sesión inexistente, y
  con el correcto. Solo el último debe recibir el saludo `connected`.
- **CORS**: preflight desde el dominio real, desde `localhost:5173` y desde un
  origen inventado. El tercero no debe recibir cabecera de permiso.
- **Rate limit**: 13 creaciones seguidas.
- **Limpieza y borrado**: borrar deja 204, y después la sesión ya no existe.

### Fase 2 — Recorridos completos (gasta LLM y Tavily)

Aquí hay que **escuchar el WebSocket mientras corre**, no solo consultar el estado
al final: el streaming es la mitad del producto.

- **El despistado**: pregunta deliberadamente vaga ("quiero saber cosas sobre
  agentes"). Debe pedir aclaración, no inventarse el alcance. Se responde, y desde
  ahí debe llegar hasta el informe. Al terminar, hacerle **dos** preguntas de
  seguimiento seguidas (una sola no prueba el multi-turno).
- **El concreto**: pregunta precisa y bien acotada. Debe ir directo al informe sin
  preguntar nada. Verificar que llegan eventos de las cuatro etapas
  (scope, supervisor, research, writer) y que los mensajes quedan persistidos.
- **El que recarga**: reconectar el WebSocket cuando la sesión ya ha terminado.
  Debe reenviar el histórico completo, no solo lo que pase a partir de ese momento.

### Fase 3 — Los bordes

- **Dedos gordos**: clave de API mal copiada. La sesión se acepta (la clave no se
  valida hasta ejecutar), pero debe acabar en `failed` en segundos, con un evento
  de error que explique el motivo y **con la clave enmascarada**.
- **El explorador**: `POST /models/discover` con su clave. Debe devolver bastantes
  más modelos que el catálogo estático, y nunca devolver la clave en la respuesta.
  Probar también con clave inválida y sin claves: ninguno debe romper.
- **El impaciente**: borrar la sesión mientras está en marcha. Debe permitirlo, no
  reaparecer después, y el backend debe seguir sano.

### Fase 4 — ¿Los controles hacen lo que prometen?

La fase que más fallos encuentra y la que más se olvida. Todo control que la
interfaz ofrece al usuario debe comprobarse **por sus efectos, no por su
aceptación**:

- Ejecuta la misma pregunta con el valor **mínimo** del slider y con el siguiente,
  y compara: número de búsquedas reales, duración, tamaño del informe.
- Cuenta los eventos de búsqueda web (`tavily`) que llegan por el WebSocket y
  contrástalos con los enlaces que aparecen en el informe. **Un informe con
  enlaces y cero búsquedas significa que el modelo se ha inventado las fuentes.**
- Comprueba que los ajustes elegidos sobreviven a los cambios de camino: lo que
  pides antes de una aclaración debe seguir vigente después de ella.

Los valores extremos que la interfaz permite (el mínimo y el máximo de cada
slider) son los que más probabilidad tienen de estar rotos, precisamente porque
nadie los usa al desarrollar.

## Regresiones obligatorias

Estos cinco fallos ya se dieron una vez en producción. Compruébalos **siempre**,
en cualquier pasada, aunque el cambio que motiva la prueba parezca no tocarlos.
El guion completo está en `references/regressions.py`.

1. **El redactor no escribe sin hallazgos.** Llama a `final_report_generation`
   con `notes=[]` y con `notes=["", "  "]`: debe lanzar `NoResearchFindingsError`,
   no devolver un informe. Y con hallazgos reales sí debe redactar, para que el
   guardián no se pase de celoso.
2. **El valor mínimo del slider investiga de verdad.** Una sesión con
   `max_iterations=1` debe producir búsquedas web reales (>0 eventos de tavily),
   no un informe instantáneo. Si termina en 15 segundos, algo está mal.
3. **El chat posterior responde.** Sesión completada → dos preguntas seguidas con
   `api_keys` en el cuerpo → deben llegar dos eventos `chat_response` y **cero**
   eventos `error`.
4. **La aclaración conserva los ajustes.** `continue_with_clarification` debe
   aceptar `max_iterations` y `max_concurrent_researchers`, meterlos en el
   `configurable`, y la ruta debe pasárselos desde la sesión guardada.
5. **El rate limit corta pero no estorba.** 13 creaciones seguidas deben acabar en
   429 tras dejar pasar las primeras, y 15 GET de listado seguidos deben responder
   200 todas: si el sondeo del navegador recibe un 429, la web muestra "failed to
   load sessions".
6. **El motivo del error llega entero.** Pide un modelo cuya clave no aportas: el
   servidor debe nombrar la variable que falta, y `client.ts` debe lanzar un
   `ApiRequestError extends Error` para que el modal lo muestre en vez del
   genérico.

Dos precauciones al ejecutarlas:

- **La prueba de rate limit va la última.** Agota la cuota de creación y hace
  fallar todo lo que venga detrás con un 429 que parece otro fallo distinto.
- Para el caso 6 elige un proveedor cuya clave **no** esté en tu entorno. Conviene
  comprobarlo antes con `os.getenv`, porque una variable exportada en la shell la
  hereda el servidor local y el caso deja de probar lo que crees.

## Detalles del entorno que confunden

- El WebSocket rechaza **en el handshake con HTTP 403**, no con un código de cierre
  4403. Si tu aserción espera `ConnectionClosed`, verás un falso fallo.
- `/models` y `/sessions` sin barra final devuelven un 307 hacia `http://`. El
  front siempre usa la barra final; úsala tú también.
- Los errores no vienen todos con la misma forma: la validación de Pydantic
  responde `{code, message, details}`, pero `HTTPException` responde `{detail}`.
- La investigación corre como **background task**: `POST /start` devuelve 200 al
  instante y el trabajo real ocurre después. Hay que sondear el estado o escuchar
  eventos; nunca dar por bueno el 200 de arranque.
- La máquina de Fly se duerme con ~3 min de inactividad. El primer arranque en
  frío tarda unos segundos: no lo confundas con un fallo.
- **No añadas `from __future__ import annotations` a `api/routes/sessions.py`.**
  Con las anotaciones en forma de cadena, el envoltorio de `slowapi` las intenta
  resolver en su propio módulo, no encuentra los modelos Pydantic y FastAPI
  degrada el cuerpo a parámetro de query: todos los POST fallan con
  "Field required" en `loc: ["query","payload"]`.
- Para levantar la API en local hay que quitar `FLY_API_KEY` del `.env`: la
  configuración de la aplicación rechaza variables desconocidas y no arranca.
  En producción no ocurre porque las variables vienen de `fly secrets`.

## Cuando algo falla, encuentra la causa

No te quedes en "el chat devolvió un error". Los logs de producción dan el
traceback exacto:

```bash
export FLY_API_TOKEN=$(grep '^FLY_API_KEY=' .env | cut -d= -f2- | tr -d '"')
fly logs --no-tail -a langgraph-deepresearcher | grep -B2 -A15 "ERROR"
```

Después confirma la causa **leyendo el código**, y cita el archivo y la línea. Un
fallo reportado sin causa raíz obliga a repetir todo el trabajo de diagnóstico.

Presta atención especial a los datos que se pierden entre capas: es el patrón de
error más frecuente aquí. La ruta recoge algo del usuario, el servicio sabe
recibirlo, pero la llamada intermedia no lo reenvía. Comprueba en cada camino
(arranque, aclaración, chat) que llegan las claves y los límites.

## La parte web

Si la extensión de Chrome tiene permiso sobre el dominio, prueba también la
interfaz: primera visita sin claves configuradas, mensajes de error visibles,
navegación entre sesiones, informe renderizado y chat posterior.

Si el navegador no responde (falta de permisos de sitio), **dilo en el informe** y
compensa revisando el código del front en `web/src/`: cómo se muestran los errores
de la API, qué se envía en cada llamada y qué controles se ofrecen. Varios fallos
de experiencia de usuario se ven leyendo esos archivos sin abrir el navegador.

## Higiene

- Genera un `X-Client-ID` único por persona simulada e **imprímelo**: sin él no
  podrás borrar después las sesiones que crees en producción.
- Borra al terminar todas las sesiones de prueba.
- **No mandes correos sin permiso explícito.** El campo `user_email` dispara un
  envío real vía Resend, que sí está configurado en producción.
- No toques secretos ni redespliegues como parte de una prueba.

## Cómo informar

Ordena por daño al usuario, no por gravedad técnica. Para cada fallo: qué ve la
persona, qué lo causa (archivo y línea) y a cuánta gente afecta. Distingue entre
lo que falla siempre y lo que falla en un caso concreto.

Di también qué **no** pudiste probar y por qué. Un informe que solo enumera
aciertos no sirve para decidir nada.

El guion de `references/harness.py` trae el esqueleto reutilizable: cliente HTTP
con cabeceras, escucha de WebSocket en segundo plano, espera de estado y
acumulador de resultados.
