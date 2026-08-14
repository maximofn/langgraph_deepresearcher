"""Regresiones obligatorias: cinco fallos que ya llegaron a producción una vez.

Ejecutar con la API levantada (por defecto en local, puerto 8124):

    cd <dir con un .env sin FLY_API_KEY>
    PYTHONPATH=<repo>:<repo>/src .venv/bin/python -m uvicorn api.main:app --port 8124
    .venv/bin/python regressions.py

Para probar contra producción, cambia BASE/WS_BASE por las URLs de fly.dev y
quita las comprobaciones que importan módulos locales (1a y 3), que solo tienen
sentido sobre el código que tienes delante.

El orden importa: la prueba de rate limit va la última porque agota la cuota.
"""

import asyncio
import json
import os
import pathlib
import sys
import time
import uuid

import httpx
import websockets

ROOT = "/Users/macm1/Documents/proyectos/langgraph_deepresearcher"
sys.path.insert(0, ROOT)
sys.path.insert(0, f"{ROOT}/src")

for line in pathlib.Path(f"{ROOT}/.env").read_text().splitlines():
    if line.startswith("OPENAI_API_KEY="):
        os.environ["USER_OPENAI_KEY"] = line.split("=", 1)[1].strip().strip('"')

KEYS = {"OPENAI_API_KEY": os.environ["USER_OPENAI_KEY"]}
ROLES = ["scope", "supervisor", "research", "compress", "summarization", "writer"]
MODELS = {r: "gpt-4.1-mini" for r in ROLES}
BASE = "http://127.0.0.1:8124"
WS_BASE = "ws://127.0.0.1:8124"

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}", flush=True)


# ---------------------------------------------------------------- FIX 1a
async def fix1a_writer_guard():
    """El redactor debe negarse a escribir sin hallazgos, en vez de inventar."""
    print("\n=== FIX 1a: el redactor rechaza informes sin investigación ===")
    from write.write_agent import NoResearchFindingsError, final_report_generation

    for nombre, notes in [("notes vacío", []),
                          ("notes con cadenas en blanco", ["", "   ", "\n"])]:
        try:
            await final_report_generation(
                {"notes": notes, "research_brief": "cualquier cosa"},
                {"configurable": {"models": MODELS, "api_keys": KEYS}},
            )
            check(f"1a: rechaza con {nombre}", False, "¡escribió un informe igualmente!")
        except NoResearchFindingsError as e:
            check(f"1a: rechaza con {nombre}", True, str(e)[:70] + "…")
        except Exception as e:
            check(f"1a: rechaza con {nombre}", False, f"error inesperado: {type(e).__name__}: {e}")

    # Con hallazgos reales sí debe escribir (que el guard no sea demasiado celoso)
    try:
        out = await final_report_generation(
            {"notes": ["Hallazgo: LangGraph modela agentes como grafos de estado."],
             "research_brief": "Explica qué es LangGraph en dos frases."},
            {"configurable": {"models": MODELS, "api_keys": KEYS}},
        )
        check("1a: con hallazgos sí redacta", len(out.get("final_report", "")) > 50,
              f"{len(out.get('final_report',''))} chars")
    except Exception as e:
        check("1a: con hallazgos sí redacta", False, f"{type(e).__name__}: {e}")


# ---------------------------------------------------------------- FIX 1b
async def fix1b_iterations(c):
    """max_iterations=1 debe producir exactamente una ronda de investigación real."""
    print("\n=== FIX 1b: max_iterations=1 investiga de verdad ===")
    cid = f"fix1b-{uuid.uuid4().hex[:6]}"
    h = {"X-Client-ID": cid}
    r = await c.post("/sessions/", json={
        "query": "¿Qué es el patrón supervisor en sistemas multiagente con LLM? Breve.",
        "max_iterations": 1, "max_concurrent_researchers": 1,
        "models": MODELS, "api_keys": KEYS,
    }, headers=h)
    sid = r.json()["session"]["id"]
    events = []

    async def watch():
        try:
            async with websockets.connect(f"{WS_BASE}/ws/{sid}?client_id={cid}",
                                          max_size=None) as ws:
                async for m in ws:
                    d = json.loads(m)
                    if d.get("type") == "event":
                        events.append(d["data"])
        except Exception:
            pass

    t = asyncio.create_task(watch())
    await asyncio.sleep(1)
    await c.post(f"/sessions/{sid}/start", headers=h)

    t0, s = time.time(), None
    while time.time() - t0 < 600:
        s = (await c.get(f"/sessions/{sid}", headers=h)).json()
        if s["status"] in ("completed", "failed", "clarification_needed"):
            break
        await asyncio.sleep(5)
    t.cancel()

    busquedas = [e for e in events if "tavily" in str(e.get("title", "")).lower()]
    informe = s.get("final_report") or ""
    check("1b: la sesión completa", s["status"] == "completed", s["status"])
    check("1b: hubo búsquedas web reales", len(busquedas) > 0,
          f"{len(busquedas)} búsquedas en {int(time.time()-t0)}s")
    check("1b: el informe se apoya en investigación",
          len(informe) > 300 and len(busquedas) > 0,
          f"{len(informe)} chars · {informe.count('http')} enlaces")
    await c.delete(f"/sessions/{sid}", headers=h)
    return sid


# ---------------------------------------------------------------- FIX 2
async def fix2_chat(c):
    """El chat posterior debe funcionar enviando las claves del usuario."""
    print("\n=== FIX 2: el chat post-investigación responde ===")
    cid = f"fix2-{uuid.uuid4().hex[:6]}"
    h = {"X-Client-ID": cid}
    r = await c.post("/sessions/", json={
        "query": "¿Qué es LangGraph? Respuesta muy breve.",
        "max_iterations": 1, "max_concurrent_researchers": 1,
        "models": MODELS, "api_keys": KEYS,
    }, headers=h)
    sid = r.json()["session"]["id"]
    events = []

    async def watch():
        try:
            async with websockets.connect(f"{WS_BASE}/ws/{sid}?client_id={cid}",
                                          max_size=None) as ws:
                async for m in ws:
                    d = json.loads(m)
                    if d.get("type") == "event":
                        events.append(d["data"])
        except Exception:
            pass

    t = asyncio.create_task(watch())
    await asyncio.sleep(1)
    await c.post(f"/sessions/{sid}/start", headers=h)
    t0, s = time.time(), None
    while time.time() - t0 < 600:
        s = (await c.get(f"/sessions/{sid}", headers=h)).json()
        if s["status"] in ("completed", "failed", "clarification_needed"):
            break
        await asyncio.sleep(5)

    if s["status"] != "completed":
        check("2: sesión lista para chatear", False, s["status"])
        t.cancel()
        return

    # Con claves: debe responder
    n = len(events)
    r = await c.post(f"/sessions/{sid}/chat",
                     json={"message": "Resúmelo en una frase.", "api_keys": KEYS},
                     headers=h)
    check("2: el endpoint acepta api_keys", r.status_code == 200, f"got {r.status_code}")
    t0 = time.time()
    while time.time() - t0 < 180:
        if any(e.get("event_type") == "chat_response" for e in events[n:]):
            break
        await asyncio.sleep(3)
    respuestas = [e for e in events[n:] if e.get("event_type") == "chat_response"]
    errores = [e for e in events[n:] if e.get("event_type") == "error"]
    check("2: llega la respuesta del chat", bool(respuestas) and not errores,
          (respuestas[0].get("content") or "")[:90] if respuestas
          else f"errores: {[e.get('title') for e in errores]}")

    # Segunda pregunta: multi-turno
    n = len(events)
    await c.post(f"/sessions/{sid}/chat",
                 json={"message": "¿Y su mayor limitación?", "api_keys": KEYS}, headers=h)
    t0 = time.time()
    while time.time() - t0 < 180:
        if any(e.get("event_type") == "chat_response" for e in events[n:]):
            break
        await asyncio.sleep(3)
    check("2: multi-turno funciona",
          any(e.get("event_type") == "chat_response" for e in events[n:]), "")

    t.cancel()
    await c.delete(f"/sessions/{sid}", headers=h)


# ---------------------------------------------------------------- FIX 3
async def fix3_clarify_limits():
    """Los límites del usuario deben viajar también en la ruta de aclaración."""
    print("\n=== FIX 3: la aclaración conserva los ajustes ===")
    import inspect

    from api.services.research_service import ResearchService

    sig = inspect.signature(ResearchService.continue_with_clarification)
    check("3: continue_with_clarification acepta los límites",
          "max_iterations" in sig.parameters
          and "max_concurrent_researchers" in sig.parameters,
          str(list(sig.parameters))[:90])

    src = inspect.getsource(ResearchService.continue_with_clarification)
    check("3: y los mete en el configurable",
          'configurable["max_iterations"]' in src
          and 'configurable["max_concurrent_researchers"]' in src, "")

    from api.routes import sessions as routes
    src_route = inspect.getsource(routes._continue_research_bg)
    check("3: la ruta se los pasa desde la sesión guardada",
          "session.max_iterations" in src_route
          and "session.max_concurrent_researchers" in src_route, "")


# ---------------------------------------------------------------- FIX 4
async def fix4_rate_limit(c):
    """Crear sesiones en bucle debe acabar en 429."""
    print("\n=== FIX 4: el rate limit corta el abuso ===")
    cid = f"fix4-{uuid.uuid4().hex[:6]}"
    h = {"X-Client-ID": cid}
    codes, creadas = [], []
    for i in range(13):
        r = await c.post("/sessions/", json={
            "query": f"spam {i}", "models": MODELS, "api_keys": KEYS,
        }, headers=h)
        codes.append(r.status_code)
        if r.status_code == 200:
            creadas.append(r.json()["session"]["id"])
    check("4: aparece el 429", 429 in codes, f"códigos: {codes}")
    check("4: pero deja pasar las primeras", codes.count(200) >= 5,
          f"{codes.count(200)} aceptadas antes de cortar")

    # Las GET de sondeo que usa la web NO deben verse afectadas
    gets = [(await c.get("/sessions/", headers=h)).status_code for _ in range(15)]
    check("4: el sondeo de la web sigue libre", all(g == 200 for g in gets),
          f"{gets.count(200)}/15 OK")
    for sid in creadas:
        await c.delete(f"/sessions/{sid}", headers=h)


# ---------------------------------------------------------------- FIX 5
async def fix5_error_message(c):
    """El backend debe seguir explicando el motivo; el front ya sabe leerlo."""
    print("\n=== FIX 5: el motivo del error llega al usuario ===")
    h = {"X-Client-ID": f"fix5-{uuid.uuid4().hex[:6]}"}
    # kimi: su clave no está ni en el entorno local ni en producción
    r = await c.post("/sessions/", json={
        "query": "test", "models": {**MODELS, "writer": "kimi-k2-thinking"},
        "api_keys": KEYS,
    }, headers=h)
    body = r.json()
    detalle = body.get("detail") or body.get("message") or ""
    check("5: el servidor explica qué clave falta",
          r.status_code == 422 and "KIMI_K2_API_KEY" in str(detalle), str(detalle)[:90])

    client_ts = pathlib.Path(f"{ROOT}/web/src/api/client.ts").read_text()
    check("5: el cliente lanza un Error de verdad",
          "class ApiRequestError extends Error" in client_ts
          and "payload.detail" in client_ts, "")


async def main():
    await fix1a_writer_guard()
    await fix3_clarify_limits()
    async with httpx.AsyncClient(base_url=BASE, timeout=120) as c:
        await fix5_error_message(c)
        await fix1b_iterations(c)
        await fix2_chat(c)
        # El de rate limit va el último: agota la cuota para todo lo demás.
        await fix4_rate_limit(c)

    print("\n" + "=" * 60)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"RESUMEN ARREGLOS: {passed}/{len(RESULTS)} OK")
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"  FALLO: {name} — {detail}")


asyncio.run(main())
