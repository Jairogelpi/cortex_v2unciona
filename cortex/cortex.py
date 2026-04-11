from cortex import phi, kappa


def evaluar_completo(agente_fn, pregunta: str) -> dict:
    """
    Pipeline Φ → Κ completo.

    Φ factoriza en 8 dimensiones → detecta dónde falla
    Κ evalúa confianza global → decide si actuar

    Si cualquiera de los dos dice BACKTRACK → no se actúa.
    """

    print("🤖 Agente generando respuesta...")
    respuesta = agente_fn(pregunta)

    print("🔬 Φ factorizando semánticamente...")
    resultado_phi = phi.factorizar(pregunta, respuesta)
    phi.mostrar(resultado_phi)

    print("🔍 Κ evaluando confianza global...")
    resultado_kappa = kappa.evaluar(pregunta, respuesta)

    # Decisión final: ambos deben aprobar
    delta_phi = resultado_phi["delta_phi"]
    delta_kappa = resultado_kappa.get("delta", 0)
    delta_final = round((delta_phi + delta_kappa) / 2, 2)
    puede_actuar_phi = resultado_phi.get("puede_actuar", delta_phi >= 0.65)
    puede_actuar_kappa = resultado_kappa.get("puede_actuar", delta_kappa >= 0.65)
    puede_actuar = puede_actuar_phi and puede_actuar_kappa

    print(f"\n{'='*50}")
    print("VEREDICTO FINAL Φ+Κ")
    print(f"δ_phi: {delta_phi:.2f}  |  δ_kappa: {delta_kappa:.2f}  |  δ_final: {delta_final:.2f}")
    print(f"{'✅ CONFIABLE — el agente puede actuar' if puede_actuar else '🛑 BACKTRACK — el agente no actúa'}")

    if resultado_phi["dimensiones_criticas"]:
        print("\n🔴 Fallos detectados por Φ:")
        for d in resultado_phi["dimensiones_criticas"]:
            print(f"   {d['dimension']}: {d['score']:.2f} — {d['razon']}")

    if not puede_actuar_phi:
        print(f"\n🔴 Razón de Φ: {', '.join([d['dimension'] for d in resultado_phi['dimensiones_criticas']])}")

    if not puede_actuar_kappa:
        print(f"\n🔴 Razón de Κ: {resultado_kappa.get('razon', '')}")

    print(f"{'='*50}\n")

    return {
        "respuesta": respuesta if puede_actuar else None,
        "delta_phi": delta_phi,
        "delta_kappa": delta_kappa,
        "delta_final": delta_final,
        "puede_actuar": puede_actuar,
        "dimensiones_criticas": resultado_phi["dimensiones_criticas"],
        "bloqueada": not puede_actuar,
    }


def wrap(agente_fn, pregunta: str) -> dict:
    """
    Interfaz principal de Cortex.
    Envuelve cualquier agente con el pipeline Φ+Κ completo.

    Uso:
        from cortex import cortex
        resultado = cortex.wrap(mi_agente, pregunta)
    """
    return evaluar_completo(agente_fn, pregunta)