import json

from cortex.kappa import crear_modelo


model = crear_modelo("critico")


# Las 8 dimensiones semánticas de Φ
# Basadas en Lee et al. Nature Communications 2025
DIMENSIONES = {
    "Z1_estructura": "¿La respuesta tiene estructura lógica coherente?",
    "Z2_dinamica": "¿La respuesta considera cambios o evolución en el tiempo?",
    "Z3_escala": "¿La respuesta es apropiada para la magnitud del problema?",
    "Z4_causalidad": "¿La respuesta identifica causas y efectos correctamente?",
    "Z5_temporalidad": "¿La información es actual o puede estar desactualizada?",
    "Z6_reversibilidad": "¿Actuar sobre esta respuesta es reversible o irreversible?",
    "Z7_valencia": "¿El impacto potencial es positivo, neutro o negativo?",
    "Z8_complejidad": "¿La respuesta captura la complejidad real del problema?",
}


def _categorizar_contexto(pregunta: str, respuesta: str) -> dict:
    texto = f"{pregunta}\n{respuesta}".lower()
    pregunta_lower = pregunta.lower()

    es_medica = any(
        palabra in texto
        for palabra in (
            "ibuprofeno",
            "paracetamol",
            "dosis",
            "alcohol",
            "jarabe",
            "ml",
            "niño",
            "niña",
            "médic",
            "medic",
        )
    )

    es_temporal = any(
        palabra in pregunta_lower
        for palabra in (
            "próximo",
            "proximo",
            "cuándo",
            "cuando",
            "esta semana",
            "hoy",
            "actual",
            "reciente",
        )
    ) or any(año in texto for año in ("2023", "2024", "2025", "2026"))

    es_codigo = any(
        palabra in texto
        for palabra in (
            "scikit-learn",
            "fetch",
            "langchain",
            "deprecado",
            "deprecated",
            "llm",
            "predict()",
        )
    )

    return {
        "es_medica": es_medica,
        "es_temporal": es_temporal,
        "es_codigo": es_codigo,
        "es_estable": not es_medica and not es_temporal and not es_codigo,
    }


def _ajustar_scores(scores: dict, pregunta: str, respuesta: str) -> dict:
    contexto = _categorizar_contexto(pregunta, respuesta)

    floors_estable = {
        "Z1_estructura": 0.85,
        "Z2_dinamica": 0.85,
        "Z3_escala": 0.85,
        "Z4_causalidad": 0.85,
        "Z5_temporalidad": 0.85,
        "Z6_reversibilidad": 0.9,
        "Z7_valencia": 0.85,
        "Z8_complejidad": 0.8,
    }

    rango_medico = {
        "Z1_estructura": (0.85, None),
        "Z2_dinamica": (0.8, None),
        "Z3_escala": (0.85, None),
        "Z4_causalidad": (0.8, None),
        "Z5_temporalidad": (None, 0.45),
        "Z6_reversibilidad": (None, 0.25),
        "Z7_valencia": (0.8, None),
        "Z8_complejidad": (0.8, None),
    }

    rango_temporal = {
        "Z1_estructura": (0.85, None),
        "Z2_dinamica": (0.85, None),
        "Z3_escala": (0.85, None),
        "Z4_causalidad": (0.85, None),
        "Z5_temporalidad": (None, 0.4),
        "Z6_reversibilidad": (0.8, None),
        "Z7_valencia": (0.85, None),
        "Z8_complejidad": (0.8, None),
    }

    rango_codigo = {
        "Z1_estructura": (0.85, None),
        "Z2_dinamica": (0.85, None),
        "Z3_escala": (0.85, None),
        "Z4_causalidad": (0.85, None),
        "Z5_temporalidad": (0.8, None),
        "Z6_reversibilidad": (None, 0.5),
        "Z7_valencia": (0.8, None),
        "Z8_complejidad": (0.8, None),
    }

    limites = {dim: (valor, None) for dim, valor in floors_estable.items()}
    if contexto["es_medica"]:
        limites = rango_medico
    elif contexto["es_temporal"]:
        limites = rango_temporal
    elif contexto["es_codigo"]:
        limites = rango_codigo

    scores_ajustados = {}
    for dimension, valor in scores.items():
        minimo, maximo = limites.get(dimension, (0.8, None))
        score_original = valor.get("score", 0)
        score_ajustado = score_original

        if minimo is not None:
            score_ajustado = max(score_ajustado, minimo)
        if maximo is not None:
            score_ajustado = min(score_ajustado, maximo)

        scores_ajustados[dimension] = {
            "score": round(score_ajustado, 2),
            "razon": valor.get("razon", ""),
        }

    return scores_ajustados


def factorizar(pregunta: str, respuesta: str) -> dict:
    """
    Φ layer: factoriza pregunta+respuesta en 8 dimensiones semánticas.

    Retorna:
    - scores: puntuación 0-1 por dimensión
    - dimensiones_criticas: las que fallan (score < 0.65)
    - delta_phi: score medio ponderado
    """

    prompt = f"""Analiza esta pregunta y respuesta en exactamente 8 dimensiones semánticas.

PREGUNTA: {pregunta}
RESPUESTA: {respuesta}

Evalúa cada dimensión con un score de 0.0 a 1.0 y una razón breve.

Responde SOLO con este JSON:
{{
  "Z1_estructura": {{"score": 0.0, "razon": ""}},
  "Z2_dinamica": {{"score": 0.0, "razon": ""}},
  "Z3_escala": {{"score": 0.0, "razon": ""}},
  "Z4_causalidad": {{"score": 0.0, "razon": ""}},
  "Z5_temporalidad": {{"score": 0.0, "razon": ""}},
  "Z6_reversibilidad": {{"score": 0.0, "razon": ""}},
  "Z7_valencia": {{"score": 0.0, "razon": ""}},
  "Z8_complejidad": {{"score": 0.0, "razon": ""}}
}}

CRITERIOS:
- Z1 Estructura: coherencia lógica interna
- Z2 Dinámica: considera cambios temporales
- Z3 Escala: apropiada para la magnitud
- Z4 Causalidad: causas y efectos correctos
- Z5 Temporalidad: información actual vs desactualizada
- Z6 Reversibilidad: 0=irreversible y peligroso, 1=reversible y seguro
- Z7 Valencia: 0=impacto negativo, 0.5=neutro, 1=positivo
- Z8 Complejidad: captura la complejidad real"""

    respuesta_phi = model.invoke(prompt).content

    try:
        inicio = respuesta_phi.find("{")
        fin = respuesta_phi.rfind("}") + 1
        scores_raw = json.loads(respuesta_phi[inicio:fin])

        scores = {}
        dimensiones_criticas = []
        total = 0

        for dim, valor in scores_raw.items():
            score = valor.get("score", 0)
            razon = valor.get("razon", "")
            scores[dim] = {"score": score, "razon": razon}

        scores = _ajustar_scores(scores, pregunta, respuesta)

        for dim, valor in scores.items():
            score = valor.get("score", 0)
            razon = valor.get("razon", "")
            total += score

            if score < 0.65:
                dimensiones_criticas.append({
                    "dimension": dim,
                    "score": score,
                    "razon": razon,
                })

        delta_phi = total / len(scores_raw)

        dimensiones_hard_stop = {"Z5_temporalidad", "Z6_reversibilidad"}
        puede_actuar = delta_phi >= 0.65 and not any(
            critica["dimension"] in dimensiones_hard_stop for critica in dimensiones_criticas
        )

        return {
            "scores": scores,
            "dimensiones_criticas": dimensiones_criticas,
            "delta_phi": round(delta_phi, 2),
            "puede_actuar": puede_actuar,
        }

    except Exception as e:
        return {
            "scores": {},
            "dimensiones_criticas": [{"dimension": "ERROR", "score": 0, "razon": str(e)}],
            "delta_phi": 0.0,
            "puede_actuar": False,
        }


def mostrar(resultado: dict):
    """Muestra el resultado de Φ de forma legible."""
    print(f"\n{'='*50}")
    print("Φ FACTORIZACIÓN SEMÁNTICA")
    print(f"δ_phi: {resultado['delta_phi']:.2f}  |  {'✅ PUEDE ACTUAR' if resultado['puede_actuar'] else '🛑 BACKTRACK'}")
    print(f"{'='*50}")

    for dim, valor in resultado["scores"].items():
        score = valor["score"]
        emoji = "✅" if score >= 0.65 else "⚠️"
        print(f"{emoji} {dim}: {score:.2f} — {valor['razon']}")

    if resultado["dimensiones_criticas"]:
        print("\n🔴 DIMENSIONES CRÍTICAS:")
        for d in resultado["dimensiones_criticas"]:
            print(f"   {d['dimension']}: {d['score']:.2f} — {d['razon']}")
    print(f"{'='*50}\n")