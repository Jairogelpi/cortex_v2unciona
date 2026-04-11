import sys
sys.path.append(".")

from langchain_ollama import ChatOllama
from ddgs import DDGS
from cortex import kappa  # importamos el módulo

model = ChatOllama(model="qwen3:8b", temperature=0, num_predict=512)

# Agente simple — el que vamos a proteger con Κ
def mi_agente(pregunta: str) -> str:
    return model.invoke(pregunta).content

# Test 1: pregunta con respuesta que el modelo puede inventar
print("\n TEST 1: Fecha evento reciente")
resultado = kappa.wrap(mi_agente, "¿Cuándo es el próximo Red Bull Batalla?")
if resultado["bloqueada"]:
    print("🛑 Respuesta bloqueada por Κ — el agente no habría actuado")
else:
    print(f"✅ Respuesta aprobada:\n{resultado['respuesta']}")

# Test 2: pregunta factual estable
print("\n TEST 2: Hecho estable")
resultado = kappa.wrap(mi_agente, "¿Cuántos países hay en la Unión Europea?")
if resultado["bloqueada"]:
    print("🛑 Respuesta bloqueada")
else:
    print(f"✅ Respuesta aprobada:\n{resultado['respuesta']}")
