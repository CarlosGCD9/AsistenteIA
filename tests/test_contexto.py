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

    instancia = AgenteIA.__new__(AgenteIA)
    instancia.persistencia = Mock()
    instancia.persistencia.cargar_memoria.return_value = {}
    return instancia


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

    agente.llm = Mock()

    with pytest.raises(ValueError):
        agente.responder("qq")

    agente.persistencia.guardar_mensaje.assert_not_called()
    agente.llm.responder.assert_not_called()

    assert agente.messages == [
        {"role": "system", "content": "ss"}
    ]

def test_contexto_incluye_memoria(agente):
    agente.persistencia.cargar_memoria.return_value = {"usuario": "Carlos"}

    agente.messages = [
        {"role": "system", "content": "sistema"},
        {"role": "user", "content": "¿Cómo me llamo?"}
    ]

    contexto = agente._construir_contexto()

    assert "usuario: Carlos" in contexto[0]["content"]
    assert agente.messages[0]["content"] == "sistema"

def test_memoria_excesiva_rechaza_sin_guardar(agente, monkeypatch):
    monkeypatch.setattr(modulo_agente, maximo_contexto_chars, 100)

    agente.persistencia.cargar_memoria.return_value = {
        "dato": "x" * 101
    }

    agente.messages = [
        {"role": "system", "content": "s"}
    ]

    agente.llm = Mock()

    with pytest.raises(ValueError):
        agente.responder("q")

    agente.persistencia.guardar_mensaje.assert_not_called()
    agente.llm.responder.assert_not_called()

    assert agente.messages == [
        {"role": "system", "content": "s"}
    ]

def test_guardar_recuerdo_elimina_espacios(agente):
    respuesta = agente._guardar_recuerdo(" usuario = Carlos ")

    agente.persistencia.guardar_memoria.assert_called_once_with(
        "usuario", "Carlos"
    )
    assert respuesta == "Recordado: usuario = Carlos"

def test_guardar_recuerdo_rechaza_valor_vacio(agente):
    with pytest.raises(ValueError):
        agente._guardar_recuerdo("usuario=   ")

    agente.persistencia.guardar_memoria.assert_not_called()

def test_eliminar_recuerdo_elimina_espacios(agente):
    agente.persistencia.eliminar_memoria.return_value = True

    eliminar = agente._eliminar_recuerdo(" usuario ")

    agente.persistencia.eliminar_memoria.assert_called_once_with("usuario")

    assert eliminar == "Olvidado: usuario"


def test_eliminar_recuerdo_rechaza_clave_vacia(agente):
    with pytest.raises(ValueError):
        agente._eliminar_recuerdo("   ")

    agente.persistencia.eliminar_memoria.assert_not_called()


def test_eliminar_recuerdo_inexistente(agente):
    agente.persistencia.eliminar_memoria.return_value = False

    respuesta = agente._eliminar_recuerdo("no_existe")

    agente.persistencia.eliminar_memoria.assert_called_once_with("no_existe")
    assert respuesta == "No existe el recuerdo: no_existe"


def test_consola_olvidar_no_consulta_llm(agente, monkeypatch, capsys):
    agente.messages = [{"role": "system", "content": "Sistema"}]
    agente.llm = Mock()
    agente.persistencia.eliminar_memoria.return_value = True
    entrada = Mock(side_effect=["/olvidar usuario", "salir"])
    monkeypatch.setattr("builtins.input", entrada)

    agente.ejecutar()

    agente.persistencia.eliminar_memoria.assert_called_once_with("usuario")
    agente.llm.responder.assert_not_called()
    agente.persistencia.guardar_mensaje.assert_not_called()
    assert agente.messages == [{"role": "system", "content": "Sistema"}]
    assert "Olvidado: usuario" in capsys.readouterr().out
