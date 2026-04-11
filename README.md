# cortex-ai

Un agente que no sabe cuándo equivocarse no es un agente. Es un riesgo.

## Qué es

Cortex AI es un paquete con tres capas:

- `Κ` evalúa confianza global y decide si una respuesta puede usarse.
- `Φ` factoriza una respuesta en 8 dimensiones semánticas y diagnostica dónde falla.
- `Φ+Κ` combina ambos en un pipeline que sólo deja actuar al agente si los dos aprueban.

## Instalación

```bash
pip install -e .
```

Si se publica en PyPI, también funcionará:

```bash
pip install cortex-ai
```

## Configuración del modelo

Por defecto Cortex usa Ollama con `qwen3:8b`.

Si defines `OPENROUTER_API_KEY`, usa OpenRouter automáticamente y deja Ollama como fallback.

Variables útiles:

- `OPENROUTER_API_KEY`: activa OpenRouter.
- `CORTEX_PROVIDER`: fuerza `openrouter` o `ollama`.
- `CORTEX_OPENROUTER_MODEL`: modelo remoto a usar, por defecto `openai/gpt-4o-mini`.
- `CORTEX_OLLAMA_MODEL`: modelo local a usar, por defecto `qwen3:8b`.

## API

### Κ: crítica de confianza

```python
from cortex import kappa

def mi_agente(pregunta):
    return mi_modelo.invoke(pregunta)

resultado = kappa.wrap(mi_agente, "¿cuándo es el próximo Red Bull Batalla?")
```

`kappa.wrap()` devuelve un diccionario con:

- `respuesta`: texto aprobado o `None`.
- `evaluacion`: objeto con `delta`, `veredicto`, `razon` y `problemas`.
- `bloqueada`: `True` si no debe actuar.

### Φ: factorización semántica

```python
from cortex import phi

resultado = phi.factorizar(pregunta, respuesta)
phi.mostrar(resultado)
```

`phi.factorizar()` devuelve:

- `scores`: puntuación por dimensión `Z1` a `Z8`.
- `dimensiones_criticas`: dimensiones con fallo.
- `delta_phi`: media semántica global.
- `puede_actuar`: decisión preliminar.

### Φ+Κ: pipeline completo

```python
from cortex import cortex

resultado = cortex.wrap(mi_agente, pregunta)
```

`cortex.wrap()` exige que Φ y Κ aprueben. Si uno falla, el agente no actúa.

## Dimensiones de Φ

Φ factoriza la respuesta en estas 8 dimensiones ortogonales:

- `Z1_estructura`: coherencia lógica.
- `Z2_dinamica`: cambios o evolución temporal.
- `Z3_escala`: magnitud apropiada del problema.
- `Z4_causalidad`: causas y efectos correctos.
- `Z5_temporalidad`: vigencia o desactualización.
- `Z6_reversibilidad`: si actuar es reversible o peligroso.
- `Z7_valencia`: impacto potencial.
- `Z8_complejidad`: si captura la complejidad real.

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

## Tests

```bash
python test_kappa.py
python test_phi.py
python test_cortex.py
```

- `test_kappa.py`: smoke test de Κ.
- `test_phi.py`: factoriza las 8 dimensiones y muestra fallos.
- `test_cortex.py`: pipeline completo Φ+Κ.

## El problema que resuelve

Hoy los agentes responden con confianza uniforme.
Inventan fechas, herramientas y datos sin advertencia.

Probamos esto en vivo:

- Pregunta: ¿Cuándo es el próximo Red Bull Batalla?
- Agente: puede inventar o desactualizar la fecha.
- Κ layer: bloquea si no hay confianza suficiente.

Ningún framework resuelve esto de forma nativa, local y agnóstica.

## Por qué no es LangSmith ni Phoenix

- LangSmith: observabilidad post-hoc, requiere LangChain y SaaS.
- Phoenix: trazas técnicas, no evaluación semántica en tiempo real.
- Κ layer: actúa antes de que el agente ejecute, de forma local, y funciona con cualquier framework.

## Requisitos

- Python 3.10+
- Ollama local o OpenRouter con `OPENROUTER_API_KEY`
- Modelo recomendado: `qwen3:8b` local o `openai/gpt-4o-mini` vía OpenRouter

## Fundamento

Basado en Cortex V2, una arquitectura agentiva de 10 capas inspirada en neurociencia.
El Κ layer replica el OFC (orbitofrontal cortex): un evaluador independiente que calibra sin el sesgo del agente que tomó la decisión.

Paper completo: osf.io/wdkcx

## Licencia

MIT — Jairogelpi 2026