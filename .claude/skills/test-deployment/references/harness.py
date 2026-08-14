"""Esqueleto reutilizable para las pruebas de extremo a extremo.

Copia este archivo al scratchpad, añade tus personas y ejecútalo con
`.venv/bin/python`. No lo ejecutes tal cual: `demo()` solo enseña el uso.

Cubre lo aburrido y propenso a error: cabeceras, claves desde .env, escucha
del WebSocket en segundo plano, espera de estado y recuento de resultados.
"""

import asyncio
import json
import os
import pathlib
import time
import uuid

import httpx
import websockets

# --------------------------------------------------------------------------
# Entorno
# --------------------------------------------------------------------------

PROD = "https://langgraph-deepresearcher.fly.dev"
PROD_WS = "wss://langgraph-deepresearcher.fly.dev"
LOCAL = "http://localhost:8000"
LOCAL_WS = "ws://localhost:8000"

BASE, WS_BASE = PROD, PROD_WS

ROLES = ["scope", "supervisor", "research", "compress", "summarization", "writer"]
CHEAP_MODELS = {r: "gpt-4.1-mini" for r in ROLES}

PROJECT_ROOT = pathlib.Path(
    os.environ.get("DEEPRESEARCHER_ROOT",
                   "/Users/macm1/Documents/proyectos/langgraph_deepresearcher")
)
ENV_PATH = PROJECT_ROOT / ".env"


def load_user_keys(*names):
    """Lee del .env las claves que el usuario pegaría en Settings.

    Producción no tiene claves de LLM: sin esto, toda creación de sesión da 422.
    """
    wanted = set(names) or {"OPENAI_API_KEY"}
    keys = {}
    for line in ENV_PATH.read_text().splitlines():
        name, _, value = line.partition("=")
        if name in wanted and value.strip():
            keys[name] = value.strip().strip('"').strip("'")
    missing = wanted - keys.keys()
    if missing:
        raise SystemExit(f"Faltan en {ENV_PATH}: {sorted(missing)}")
    return keys


# --------------------------------------------------------------------------
# Resultados
# --------------------------------------------------------------------------

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}", flush=True)


def summary(titulo="RESUMEN"):
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print("\n" + "=" * 60)
    print(f"{titulo}: {passed}/{len(RESULTS)} OK")
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"  FALLO: {name} — {detail}")
    return passed == len(RESULTS)


# --------------------------------------------------------------------------
# Persona: un cliente con su propio X-Client-ID
# --------------------------------------------------------------------------


class Persona:
    """Un usuario simulado. El client_id se imprime para poder limpiar luego."""

    def __init__(self, nombre):
        self.nombre = nombre
        self.client_id = f"test-{nombre}-{uuid.uuid4().hex[:8]}"
        self.headers = {"X-Client-ID": self.client_id}
        self.sessions = []
        print(f"\n=== PERSONA: {nombre}  (client_id={self.client_id}) ===", flush=True)

    async def crear(self, c, query, api_keys, **kwargs):
        payload = {
            "query": query,
            "models": kwargs.pop("models", CHEAP_MODELS),
            "api_keys": api_keys,
            **kwargs,
        }
        r = await c.post("/sessions/", json=payload, headers=self.headers)
        if r.status_code == 200:
            sid = r.json()["session"]["id"]
            self.sessions.append(sid)
            print(f"  sesión {sid}", flush=True)
        return r

    async def estado(self, c, sid):
        return (await c.get(f"/sessions/{sid}", headers=self.headers)).json()

    async def esperar(self, c, sid, objetivos, timeout=900):
        """Sondea hasta alcanzar uno de los estados objetivo. Devuelve la sesión."""
        t0, ultimo, s = time.time(), None, None
        while time.time() - t0 < timeout:
            s = await self.estado(c, sid)
            if s["status"] != ultimo:
                print(f"    status -> {s['status']}  ({int(time.time()-t0)}s)", flush=True)
                ultimo = s["status"]
            if s["status"] in objetivos:
                return s
            await asyncio.sleep(5)
        return s

    async def limpiar(self, c):
        for sid in self.sessions:
            await c.delete(f"/sessions/{sid}", headers=self.headers)


# --------------------------------------------------------------------------
# WebSocket
# --------------------------------------------------------------------------


class Watcher:
    """Escucha eventos en segundo plano, como hace la web.

    Conéctalo ANTES de arrancar la investigación o perderás los primeros eventos.
    """

    def __init__(self, sid, client_id, verbose=True):
        self.sid, self.client_id, self.verbose = sid, client_id, verbose
        self.events = []
        self._task = None

    async def _run(self):
        try:
            async with websockets.connect(
                f"{WS_BASE}/ws/{self.sid}?client_id={self.client_id}",
                ping_interval=20, max_size=None,
            ) as ws:
                async for msg in ws:
                    m = json.loads(msg)
                    if m.get("type") == "event":
                        self.events.append(m["data"])
                        if self.verbose:
                            print(f"    · [{m['data'].get('event_type')}] "
                                  f"{str(m['data'].get('title'))[:70]}", flush=True)
        except Exception as e:
            print(f"    (WS cerrado: {type(e).__name__}: {e})", flush=True)

    def start(self):
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def types(self):
        return {e.get("event_type") for e in self.events}

    def busquedas_reales(self):
        """Búsquedas web efectivas. Si es 0, el informe no está investigado."""
        return [e for e in self.events if "tavily" in str(e.get("title", "")).lower()]

    def de_tipo(self, tipo):
        return [e for e in self.events if e.get("event_type") == tipo]


async def replay(sid, client_id, segundos=25):
    """Reconecta y recoge el histórico reenviado (el caso 'recargo la página')."""
    recibidos = []
    async with websockets.connect(f"{WS_BASE}/ws/{sid}?client_id={client_id}",
                                  max_size=None) as ws:
        t0 = time.time()
        while time.time() - t0 < segundos:
            try:
                m = json.loads(await asyncio.wait_for(ws.recv(), timeout=8))
            except asyncio.TimeoutError:
                break
            if m.get("type") == "event":
                recibidos.append(m["data"])
    return recibidos


# --------------------------------------------------------------------------
# Uso
# --------------------------------------------------------------------------


async def demo():
    keys = load_user_keys("OPENAI_API_KEY")
    async with httpx.AsyncClient(base_url=BASE, timeout=120) as c:
        p = Persona("concreto")
        r = await p.crear(c, "¿Qué es LangGraph?", keys,
                          max_iterations=3, max_concurrent_researchers=2)
        check("crea la sesión", r.status_code == 200, f"got {r.status_code}")
        sid = r.json()["session"]["id"]

        w = Watcher(sid, p.client_id)
        w.start()
        await asyncio.sleep(1)          # deja que el WS se establezca
        await c.post(f"/sessions/{sid}/start", headers=p.headers)

        s = await p.esperar(c, sid, {"completed", "failed", "clarification_needed"})
        check("termina la investigación", s["status"] == "completed", s["status"])

        # Un informe largo NO prueba que se haya investigado:
        informe = s.get("final_report") or ""
        check("el informe está realmente investigado",
              len(w.busquedas_reales()) > 0 or "http" not in informe,
              f"{len(w.busquedas_reales())} búsquedas · {informe.count('http')} enlaces")

        await w.stop()
        await p.limpiar(c)
    summary()


if __name__ == "__main__":
    asyncio.run(demo())
