import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from cortex import kappa

model = kappa.crear_modelo("agente")


# Agente periodista sin Κ — responde siempre con confianza
def agente_sin_critico(pregunta: str) -> str:
    prompt = f"""Eres un periodista deportivo. Responde con la información más reciente que conozcas.
Pregunta: {pregunta}
Responde en 2-3 frases como si fuera una noticia."""
    return model.invoke(prompt).content


# Agente periodista con Κ — bloqueado si no puede verificar
def agente_con_critico(pregunta: str) -> dict:
    return kappa.wrap(agente_sin_critico, pregunta)


# Las noticias a verificar
noticias = [
    "¿Es cierto que Mbappé ha sido vendido por el Real Madrid esta semana?",
    "¿Cuándo es el próximo Clásico Real Madrid vs Barcelona?",
    "¿Ha ganado España algún título en 2026?",
]

print("\n" + "=" * 60)
print("DEMO 1: Agente periodista con y sin crítico Κ")
print("=" * 60)

for noticia in noticias:
    print(f"\n📰 NOTICIA: {noticia}")
    print("-" * 60)

    # Sin crítico
    print("❌ SIN Κ:")
    respuesta_raw = agente_sin_critico(noticia)
    print(f"   {respuesta_raw[:200]}")

    # Con crítico
    print("\n✅ CON Κ:")
    resultado = agente_con_critico(noticia)
    if resultado["bloqueada"]:
        print("   🛑 BLOQUEADA — el agente no habría publicado esto")
        print(f"   δ: {resultado['evaluacion']['delta']:.2f} | {resultado['evaluacion']['razon']}")
    else:
        print(f"   ✅ APROBADA — δ: {resultado['evaluacion']['delta']:.2f}")
        print(f"   {resultado['respuesta'][:200]}")

    print("-" * 60)

# Caso de control: un hecho estable que sí debería aprobarse
control = "¿Cuántos países hay en la Unión Europea?"
print(f"\n🧪 CONTROL: {control}")
print("-" * 60)

print("❌ SIN Κ:")
respuesta_raw = agente_sin_critico(control)
print(f"   {respuesta_raw[:200]}")

print("\n✅ CON Κ:")
resultado = agente_con_critico(control)
if resultado["bloqueada"]:
    print(f"   🛑 BLOQUEADA — δ: {resultado['evaluacion']['delta']:.2f} | {resultado['evaluacion']['razon']}")
else:
    print(f"   ✅ APROBADA — δ: {resultado['evaluacion']['delta']:.2f}")
    print(f"   {resultado['respuesta'][:200]}")

print("-" * 60)