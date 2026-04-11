# cortex-ai

Un agente que no sabe cuándo equivocarse no es un agente. Es un riesgo.

**Κ layer** evalúa cualquier respuesta antes de actuar.
Si δ < 0.65 → bloquea. Si δ ≥ 0.65 → aprueba.

## Instalación

```bash
pip install -e .
```

Si después lo publicamos en PyPI, también servirá:

```bash
pip install cortex-ai
```

## Velocidad

Si defines `OPENROUTER_API_KEY`, Cortex usa OpenRouter automáticamente y deja Ollama como fallback.
Por defecto usa `openai/gpt-4o-mini`, y puedes cambiarlo con `CORTEX_OPENROUTER_MODEL`.

## Uso

```python
from cortex import kappa

def mi_agente(pregunta):
    return mi_modelo.invoke(pregunta)

resultado = kappa.wrap(mi_agente, "¿cuándo es el próximo Red Bull Batalla?")
# δ 0.40 → BACKTRACK. El agente no actúa.
```

## Demos

Desde la raíz del repositorio:

```bash
python examples/demo1_noticias.py
python examples/demo2_medicina.py
python examples/demo3_codigo.py
```

- `demo1_noticias.py`: noticias y eventos recientes.
- `demo2_medicina.py`: consultas médicas de riesgo y control anatómico estable.
- `demo3_codigo.py`: recomendaciones de código y bloqueo de APIs deprecadas.

### Resumen rápido

| Demo | Bloquea | Aprueba |
| --- | --- | --- |
| `demo1_noticias.py` | Clásico Real Madrid vs Barcelona; España en 2026 | Mbappé; control de países de la UE |
| `demo2_medicina.py` | Ibuprofeno sin concentración; paracetamol + alcohol | Huesos del cuerpo humano adulto |
| `demo3_codigo.py` | `LangChain .get()` deprecado | `predict()` de scikit-learn; `fetch` moderno |

## El problema que resuelve

Hoy los agentes responden siempre con la misma confianza.
Inventan fechas, herramientas y datos — sin advertencia, sin duda.

Probamos esto en vivo:

- Pregunta: ¿Cuándo es el próximo Red Bull Batalla?
- Agente: dio una fecha de 2023 con total seguridad
- Κ layer: δ 0.40 → BACKTRACK. Respuesta bloqueada.

Ningún framework resuelve esto de forma nativa, local y agnóstica.

## Por qué no es LangSmith ni Phoenix

- LangSmith: observabilidad post-hoc, requiere LangChain, SaaS
- Phoenix: trazas técnicas, no evaluación semántica en tiempo real
- Κ layer: actúa ANTES de que el agente ejecute. Local. 3 líneas. Cualquier framework.

## Requisitos

- Python 3.10+
- Ollama corriendo localmente (ollama.ai)
- O OpenRouter con `OPENROUTER_API_KEY`
- Modelo recomendado: qwen3:8b

## Fundamento

Basado en Cortex V2 — arquitectura agentiva de 10 capas inspirada en neurociencia.
El Κ layer replica el OFC (orbitofrontal cortex): evaluador independiente que calibra
sin el sesgo del agente que tomó la decisión.

Paper completo: osf.io/wdkcx

## Licencia

MIT — Jairogelpi 2026