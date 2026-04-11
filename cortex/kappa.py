import json
import os
from functools import lru_cache
from typing import Literal

from ddgs import DDGS


@lru_cache(maxsize=None)
def crear_modelo(uso: Literal["agente", "critico"] = "critico"):
    proveedor = os.getenv("CORTEX_PROVIDER", "auto").strip().lower()
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()

    if proveedor == "openrouter" or (proveedor == "auto" and openrouter_key):
        from langchain_openai import ChatOpenAI

        model_name = os.getenv(
            "CORTEX_OPENROUTER_MODEL",
            "openai/gpt-4o-mini" if uso == "agente" else "openai/gpt-4o-mini",
        )
        return ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": os.getenv(
                    "OPENROUTER_HTTP_REFERER",
                    "https://github.com/Jairogelpi/cortex_v2unciona",
                ),
                "X-Title": os.getenv("OPENROUTER_TITLE", "cortex-ai"),
            },
        )

    from langchain_ollama import ChatOllama

    model_name = os.getenv(
        "CORTEX_OLLAMA_MODEL",
        "qwen3:8b",
    )
    ollama_kwargs = {
        "model": model_name,
        "temperature": 0,
    }
    if uso == "critico":
        ollama_kwargs["num_predict"] = int(os.getenv("CORTEX_NUM_PREDICT", "512"))
        ollama_kwargs["format"] = "json"

    return ChatOllama(**ollama_kwargs)


model = crear_modelo("critico")


def es_consulta_medica(pregunta: str) -> bool:
    texto = pregunta.lower()
    palabras_clave = (
        "ibuprofeno",
        "paracetamol",
        "alcohol",
        "dosis",
        "medic",
        "médic",
        "niño",
        "niña",
        "ml",
    )
    return any(palabra in texto for palabra in palabras_clave)

def buscar_evidencia(query: str) -> str:
    """Busca evidencia real para verificar una respuesta."""
    try:
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, max_results=3))
        if not resultados:
            return "Sin resultados"
        return "\n".join([f"- {r['title']}: {r['body'][:200]}" for r in resultados])
    except Exception as e:
        return f"Error: {e}"

def evaluar(pregunta: str, respuesta: str, verificar_web: bool = True) -> dict:
    """
    Κ layer: evalúa si una respuesta es confiable.
    Retorna δ score entre 0 y 1, y decide si el agente puede actuar.
    
    δ >= 0.65 → CONFIABLE, el agente puede actuar
    δ <  0.65 → BACKTRACK, el agente no debe actuar
    """
    
    evidencia = ""
    if verificar_web:
        evidencia = buscar_evidencia(pregunta)

    contexto_medico = ""
    if es_consulta_medica(pregunta):
        contexto_medico = """
CONTEXTO MÉDICO DE ALTO RIESGO:
- Trata esta pregunta con máxima cautela.
- Una respuesta sólo debe aprobarse si la evidencia externa confirma explícitamente la pauta.
- Si la respuesta da una dosis concreta, una conversión a mL, o minimiza una interacción entre medicamento y alcohol, usa BACKTRACK salvo verificación inequívoca.
- En dudas de dosificación pediátrica o combinaciones con alcohol, prioriza seguridad sobre completitud.
"""
    
    prompt = f"""Evalúa si esta respuesta es correcta y confiable.

{contexto_medico if contexto_medico else ""}

PREGUNTA: {pregunta}
RESPUESTA DEL AGENTE: {respuesta}
EVIDENCIA EXTERNA: {evidencia if evidencia else "No disponible"}

Responde SOLO con este JSON (sin texto adicional):
{{
  "delta": 0.0,
  "veredicto": "CONFIABLE o BACKTRACK",
  "razon": "explicación breve",
  "problemas": ["problema 1", "problema 2"]
}}

CRITERIOS para delta:
- 0.9-1.0: información verificada y reciente
- 0.7-0.9: probablemente correcta, minor gaps
- 0.5-0.7: dudosa, información no verificada
- 0.0-0.5: incorrecta o inventada

Si delta < 0.65 el veredicto debe ser BACKTRACK."""

    respuesta_kappa = model.invoke(prompt).content
    
    try:
        inicio = respuesta_kappa.find("{")
        fin = respuesta_kappa.rfind("}") + 1
        resultado = json.loads(respuesta_kappa[inicio:fin])
        resultado["puede_actuar"] = resultado.get("delta", 0) >= 0.65
        return resultado
    except:
        return {
            "delta": 0.0,
            "veredicto": "BACKTRACK",
            "razon": "Error parseando evaluación",
            "problemas": ["Error interno de Κ"],
            "puede_actuar": False
        }


def wrap(agente_fn, pregunta: str) -> dict:
    """
    Envuelve cualquier agente con el critic Κ.
    Si δ < 0.65, bloquea la respuesta y hace backtrack.
    
    Uso:
        resultado = kappa.wrap(mi_agente, "¿cuándo es el próximo Red Bull Batalla?")
    """
    print("🤖 Agente generando respuesta...")
    respuesta = agente_fn(pregunta)
    
    print("🔍 Κ evaluando confianza...")
    evaluacion = evaluar(pregunta, respuesta)
    
    delta = evaluacion.get("delta", 0)
    puede_actuar = evaluacion.get("puede_actuar", False)
    
    print(f"\n{'='*50}")
    print(f"δ score: {delta:.2f}  |  {'✅ CONFIABLE' if puede_actuar else '🛑 BACKTRACK'}")
    print(f"Razón: {evaluacion.get('razon', '')}")
    if evaluacion.get("problemas"):
        for p in evaluacion["problemas"]:
            print(f"  ⚠️  {p}")
    print(f"{'='*50}\n")
    
    return {
        "respuesta": respuesta if puede_actuar else None,
        "evaluacion": evaluacion,
        "bloqueada": not puede_actuar
    }