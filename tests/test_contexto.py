from app.agente import AgenteIA
import app.agente as modulo_agente
import pytest
from unittest.mock import Mock

maximo_contexto_turno = "MAX_CONTEXT_TURNS"
maximo_contexto_chars = "MAX_CONTEXT_CHARS"

@pytest.fixture
def agente(monkeypatch):
    monkeypatch.setattr(modulo_agente, maximo_contexto_turno, 5)
    monkeypatch.setattr(modulo_agente, maximo_contexto_chars, 12000)

    return AgenteIA.__new__(AgenteIA)


def test_contexto_excluye_pregunta_sin_respuesta(agente):
    agente.messages = [
        {"role": "system", "content": "sistema"},
        {"role": "user", "content": "pregunta sin respuesta"},
        {"role": "user", "content": "pregunta contestada"},
        {"role": "assistant", "content": "respuesta anterior"},
        {"role": "user", "content": "pregunta actual"}
    ]

    contexto = agente._construir_contexto()

    esperado = [
        {"role": "system", "content": "sistema"},
        {"role": "user", "content": "pregunta contestada"},
        {"role": "assistant", "content": "respuesta anterior"},
        {"role": "user", "content": "pregunta actual"}
    ]

    assert contexto == esperado

def test_contexto_con_limite_cero(agente, monkeypatch):
    monkeypatch.setattr(modulo_agente, maximo_contexto_turno, 0)

    agente.messages = [
        {"role": "system", "content": "sistema"},
        {"role": "user", "content": "pregunta contestada"},
        {"role": "assistant", "content": "respuesta anterior"},
        {"role": "user", "content": "pregunta actual"}
    ]

    contexto = agente._construir_contexto()

    esperado = [
        {"role": "system", "content": "sistema"},
        {"role": "user", "content": "pregunta actual"}
    ]

    assert contexto == esperado

def test_contexto_conserva_ultimos_turnos(agente, monkeypatch):

    monkeypatch.setattr(modulo_agente, maximo_contexto_turno, 2)

    agente.messages = [
        {"role": "system", "content": "sistema"},
        {"role": "user", "content": "pregunta 1"},
        {"role": "assistant", "content": "respuesta 1"},
        {"role": "user", "content": "pregunta 2"},
        {"role": "assistant", "content": "respuesta 2"},
        {"role": "user", "content": "pregunta 3"},
        {"role": "assistant", "content": "respuesta 3"},
        {"role": "user", "content": "pregunta actual"}
    ]

    esperado = [
        {"role": "system", "content": "sistema"},
        {"role": "user", "content": "pregunta 2"},
        {"role": "assistant", "content": "respuesta 2"},
        {"role": "user", "content": "pregunta 3"},
        {"role": "assistant", "content": "respuesta 3"},
        {"role": "user", "content": "pregunta actual"}
    ]

    contexto = agente._construir_contexto()

    assert contexto == esperado

def test_contexto_por_caracteres(agente, monkeypatch):
    monkeypatch.setattr(modulo_agente, maximo_contexto_chars, 6)

    agente.messages = [
        {"role": "system", "content": "s"},
        {"role": "user", "content": "aaa"},
        {"role": "assistant", "content": "bbb"},
        {"role": "user", "content": "cc"},
        {"role": "assistant", "content": "dd"},
        {"role": "user", "content": "q"},
    ]

    esperado = [
        {"role": "system", "content": "s"},
        {"role": "user", "content": "cc"},
        {"role": "assistant", "content": "dd"},
        {"role": "user", "content": "q"},
    ]

    contexto = agente._construir_contexto()

    assert contexto == esperado

def test_contexto_rechaza_base_demasiado_larga(agente, monkeypatch):
    monkeypatch.setattr(modulo_agente, maximo_contexto_chars, 3)

    agente.messages = [
        {"role": "system", "content": "ss"},
        {"role": "user", "content": "qq"},
    ]

    with pytest.raises(ValueError):
        agente._construir_contexto()

def test_responder_rechaza_sin_guardar(agente, monkeypatch):
    monkeypatch.setattr(modulo_agente, maximo_contexto_chars, 3)

    agente.messages = [
        {"role": "system", "content": "ss"}
    ]

    agente.persistencia = Mock()
    agente.llm = Mock()

    with pytest.raises(ValueError):
        agente.responder("qq")

    agente.persistencia.guardar_mensaje.assert_not_called()
    agente.llm.responder.assert_not_called()

    assert agente.messages == [
        {"role": "system", "content": "ss"}
    ]


