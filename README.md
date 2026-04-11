# cortex-ai

Un agente que no sabe cuándo equivocarse no es un agente. Es un riesgo.

**Κ layer** evalúa cualquier respuesta antes de actuar.  
Si δ < 0.65 → bloquea. Si δ ≥ 0.65 → aprueba.

## Instalación

```bash
pip install cortex-ai
```

## Uso

```python
from cortex import kappa

def mi_agente(pregunta):
    return mi_modelo.invoke(pregunta)

resultado = kappa.wrap(mi_agente, "¿cuándo es el próximo Red Bull Batalla?")
# δ 0.40 → BACKTRACK. El agente no actúa.
```

## Por qué existe

Los agentes actuales responden siempre con la misma confianza.
Inventan fechas, herramientas y datos sin advertencia.

Cortex Κ es el crítico externo que faltaba.

Funciona con cualquier agente. Cualquier framework. Local con Ollama.