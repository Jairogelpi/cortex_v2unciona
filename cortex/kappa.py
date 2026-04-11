import json
from langchain_ollama import ChatOllama
from ddgs import DDGS

model = ChatOllama(model="qwen3:8b", temperature=0, num_predict=512)

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
    
    prompt = f"""Evalúa si esta respuesta es correcta y confiable.

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