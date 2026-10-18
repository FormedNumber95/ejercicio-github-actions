"""
Tests de REGRESIÓN FUNCIONAL: los resultados del pipeline no cambian sin querer.

Se compara cada resultado clave con la referencia guardada en referencia.json.
Si alguien modifica una función y, aunque sus tests unitarios sigan pasando, el
resultado final cambia (otro top de creadores, otra media...), este test lo
detecta e indica exactamente QUÉ resultado ha cambiado.

Si el cambio es intencionado: uv run python tests/regresion/actualizar_referencia.py
"""

import pytest

from .resultados import calcular_resultados, cargar_referencia

pytestmark = pytest.mark.regresion

REFERENCIA = cargar_referencia()


@pytest.fixture(scope="module")
def resultados():
    return calcular_resultados()


def test_se_calculan_los_mismos_resultados(resultados):
    assert set(resultados) == set(REFERENCIA), "Han cambiado los resultados que se comparan: actualiza la referencia"


@pytest.mark.parametrize("clave", sorted(REFERENCIA))
def test_resultado_coincide_con_la_referencia(resultados, clave):
    esperado = REFERENCIA[clave]
    obtenido = resultados[clave]
    if isinstance(esperado, float):
        assert obtenido == pytest.approx(esperado, rel=1e-6)
    elif isinstance(esperado, dict) and all(isinstance(v, float) for v in esperado.values()):
        assert obtenido == pytest.approx(esperado, rel=1e-6)
    else:
        assert obtenido == esperado
