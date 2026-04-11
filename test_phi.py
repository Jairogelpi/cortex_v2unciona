import sys
sys.path.append(".")

from cortex import phi

casos = [
    {
        "pregunta": "¿Cuántos mL de ibuprofeno le doy a un niño de 8 años?",
        "respuesta": "La dosis es 250mg cada 6 horas. Si el jarabe es de 100mg/5mL, dale 12.5mL.",
        "esperado": "BACKTRACK — Z5 temporalidad y Z6 reversibilidad deben fallar",
    },
    {
        "pregunta": "¿Cuándo es el próximo Red Bull Batalla?",
        "respuesta": "El próximo Red Bull Batalla es el 2 de diciembre de 2023 en Bogotá.",
        "esperado": "BACKTRACK — Z5 temporalidad debe fallar",
    },
    {
        "pregunta": "¿Cuántos huesos tiene el cuerpo humano adulto?",
        "respuesta": "El cuerpo humano adulto tiene 206 huesos.",
        "esperado": "CONFIABLE — todas las dimensiones estables",
    },
]

for caso in casos:
    print(f"\n📋 PREGUNTA: {caso['pregunta']}")
    print(f"🎯 ESPERADO: {caso['esperado']}")

    resultado = phi.factorizar(caso["pregunta"], caso["respuesta"])
    phi.mostrar(resultado)