import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from cortex import kappa

model = kappa.crear_modelo("agente")


def agente_dev(pregunta: str) -> str:
    prompt = f"""Eres un desarrollador senior. Responde con código concreto y directo.
Pregunta: {pregunta}
Responde en 2-3 frases con el código exacto."""
    return model.invoke(prompt).content


def agente_dev_con_critico(pregunta: str) -> dict:
    return kappa.wrap(agente_dev, pregunta)


consultas = [
    "¿Cómo uso el método predict() de scikit-learn con un modelo entrenado?",
    "¿Cuál es la forma correcta de hacer fetch en JavaScript moderno?",
    "¿Cómo uso el método .get() deprecado de LangChain 0.1 para llamar a un LLM?",
]

print("\n" + "=" * 60)
print("DEMO 3: Agente developer con y sin crítico Κ")
print("=" * 60)

for consulta in consultas:
    print(f"\n💻 CONSULTA: {consulta}")
    print("-" * 60)

    print("❌ SIN Κ:")
    respuesta_raw = agente_dev(consulta)
    print(f"   {respuesta_raw[:200]}")

    print("\n✅ CON Κ:")
    resultado = agente_dev_con_critico(consulta)
    if resultado["bloqueada"]:
        print("   🛑 BLOQUEADA — este código podría romper producción")
        print(f"   δ: {resultado['evaluacion']['delta']:.2f} | {resultado['evaluacion']['razon']}")
    else:
        print(f"   ✅ APROBADA — δ: {resultado['evaluacion']['delta']:.2f}")
        print(f"   {resultado['respuesta'][:200]}")

    print("-" * 60)