"""
Regenera tests/regresion/referencia.json con los resultados ACTUALES del pipeline.

Úsalo SOLO cuando un cambio en los resultados sea intencionado (por ejemplo, se
corrige un error o cambian los datos de partida) y revisa el diff antes de hacer
commit: si actualizas la referencia sin pensar, el test de regresión deja de
proteger nada.

    uv run python tests/regresion/actualizar_referencia.py
"""

import json
import sys
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA.parents[1] / "scripts"))
sys.path.insert(0, str(CARPETA))

from resultados import REFERENCIA, calcular_resultados  # noqa: E402

if __name__ == "__main__":
    resultados = calcular_resultados()
    REFERENCIA.write_text(json.dumps(resultados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Referencia actualizada: {REFERENCIA} ({len(resultados)} resultados)")
