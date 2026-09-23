from app.agente import AgenteIA
import app.agente as modulo_agente
import pytest
from unittest.mock import Mock

maximo_contexto_turno = "MAX_CONTEXT_TURNS"
maximo_contexto_chars = "MAX_CONTEXT_CHARS"
limite_historial = "HISTORY_LOAD_LIMIT"

@pytest.fixture
def agente(monkeypatch):
    monkeypatch.setattr(modulo_agente, maximo_contexto_turno, 5)
    monkeypatch.setattr(modulo_agente, maximo_contexto_chars, 12000)

    instancia = AgenteIA.__new__(AgenteIA)
    instancia.persistencia = Mock()
    instancia.persistencia.cargar_memoria.return_value = {}
    instancia.persistencia.obtener_resumen.return_value = None
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


def test_resumen_excesivo_rechaza_sin_guardar(agente, monkeypatch):
    monkeypatch.setattr(modulo_agente, maximo_contexto_chars, 100)

    agente.persistencia.obtener_resumen.return_value = {
        "contenido": "x" * 101,
        "ultimo_mensaje_id": 10,
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


def test_cargar_historial_usa_limite(agente, monkeypatch):
    monkeypatch.setattr(modulo_agente, limite_historial, 3)

    agente.messages = [{"role": "system", "content": "sis"}]

    mensajes_guardados = [
        {"role": "user", "content": "hola"},
        {"role": "assistant", "content": "buenas"}
    ]  

    agente.persistencia.cargar_mensajes.return_value = mensajes_guardados
    agente._cargar_historial()

    agente.persistencia.cargar_mensajes.assert_called_once_with(limite=3)

    assert agente.messages == [
        {"role": "system", "content": "sis"},
        {"role": "user", "content": "hola"},
        {"role": "assistant", "content": "buenas"},
    ]


def test_obtener_pendientes_sin_resumen(agente):
    agente.persistencia.obtener_resumen.return_value = None
    agente.persistencia.obtener_id_inicio_historial_reciente.return_value = 12
    mensajes_pendientes = [
        {"id": 1, "role": "user", "content": "Hola"},
        {"id": 2, "role": "assistant", "content": "Buenas"},
    ]
    agente.persistencia.cargar_mensajes_para_resumen.return_value = mensajes_pendientes

    pendientes = agente._obtener_mensajes_pendientes_resumen()

    assert pendientes == mensajes_pendientes

    agente.persistencia.cargar_mensajes_para_resumen.assert_called_once_with(
        despues_de_id=0,
        antes_de_id=12,
        limite=10,
    )


def test_obtener_pendientes_continua_desde_resumen(agente):
    agente.persistencia.obtener_resumen.return_value = {
        "contenido": "Resumen anterior",
        "ultimo_mensaje_id": 5,
    }
    agente.persistencia.obtener_id_inicio_historial_reciente.return_value = 12
    mensajes_pendientes = [
        {"id": 6, "role": "user", "content": "Nuevo mensaje"},
        {"id": 7, "role": "assistant", "content": "Nueva respuesta"},
    ]
    agente.persistencia.cargar_mensajes_para_resumen.return_value = mensajes_pendientes

    assert agente._obtener_mensajes_pendientes_resumen() == mensajes_pendientes
    agente.persistencia.cargar_mensajes_para_resumen.assert_called_once_with(
        despues_de_id=5,
        antes_de_id=12,
        limite=10,
    )


def test_obtener_pendientes_sin_historial_antiguo(agente):
    agente.persistencia.obtener_resumen.return_value = None
    agente.persistencia.obtener_id_inicio_historial_reciente.return_value = None

    assert agente._obtener_mensajes_pendientes_resumen() == []
    agente.persistencia.cargar_mensajes_para_resumen.assert_not_called()


def test_formatear_mensajes_para_resumen(agente):
    mensajes = [
        {"id": 1, "role": "user", "content": "Hola"},
        {"id": 2, "role": "assistant", "content": "Buenas"},
    ]

    resultado = agente._formatear_mensajes_para_resumen(mensajes)

    assert resultado == "user: Hola\nassistant: Buenas"

def test_generar_resumen_consulta_llm(agente):
    agente.llm = Mock()
    agente.llm.responder.return_value = "Resumen actualizado"

    mensajes = [
        {"id": 2, "role": "user", "content": "Hola"}
    ]

    resultado = agente._generar_resumen(
        "Resumen anterior",
        mensajes,
    )

    peticion = agente.llm.responder.call_args.args[0]

    assert peticion[0]["role"] == "system"
    assert peticion[1]["role"] == "user"
    assert "Resumen anterior" in peticion[1]["content"]
    assert "user: Hola" in peticion[1]["content"]

    assert resultado == "Resumen actualizado"
    agente.llm.responder.assert_called_once()


def test_actualizar_resumen_guarda_resultado(agente):
    mensajes = [
        {"id": 6, "role": "user", "content": "Hola"},
        {"id": 7, "role": "assistant", "content": "Buenas"}
    ]

    agente._obtener_mensajes_pendientes_resumen = Mock(
        return_value=mensajes
    )
    agente._generar_resumen = Mock(
        return_value="Resumen actualizado"
    )

    agente.persistencia.obtener_resumen.return_value = {
        "contenido": "Resumen anterior",
        "ultimo_mensaje_id": 5,
    }

    resultado = agente._actualizar_resumen()

    assert resultado == "Resumen actualizado"

    agente._generar_resumen.assert_called_once_with(
        "Resumen anterior",
        mensajes,
    )

    agente.persistencia.guardar_resumen.assert_called_once_with(
        "Resumen actualizado",
        7,
    )


def test_obtener_pendientes_excluye_pregunta_sin_respuesta(agente):
    agente.persistencia.obtener_resumen.return_value = None
    agente.persistencia.obtener_id_inicio_historial_reciente = Mock(
        return_value=10
    )

    mensajes = [
        {"id": 1, "role": "user", "content": "Pregunta contestada"},
        {"id": 2, "role": "assistant", "content": "Respuesta"},
        {"id": 3, "role": "user", "content": "Pregunta sin respuesta"},
    ]

    agente.persistencia.cargar_mensajes_para_resumen.return_value = mensajes

    resultado = agente._obtener_mensajes_pendientes_resumen()

    assert resultado == mensajes[:2]


def test_actualizar_resumen_sin_pendientes_no_hace_nada(agente):
    agente._obtener_mensajes_pendientes_resumen = Mock(return_value=[])
    agente._generar_resumen = Mock()

    resultado = agente._actualizar_resumen()

    assert resultado is None
    agente._generar_resumen.assert_not_called()
    agente.persistencia.obtener_resumen.assert_not_called()
    agente.persistencia.guardar_resumen.assert_not_called()


def test_contexto_incluye_resumen_sin_modificar_sistema(agente):
    agente.persistencia.obtener_resumen.return_value = {
        "contenido": "El usuario está creando un asistente local",
        "ultimo_mensaje_id": 10,
    }

    agente.messages = [
        {"role": "system", "content": "Sistema original"},
        {"role": "user", "content": "¿En qué estaba trabajando?"},
    ]

    contexto = agente._construir_contexto()

    assert "El usuario está creando un asistente local" in contexto[0]["content"]
    assert agente.messages[0]["content"] == "Sistema original"



def test_consola_resumir_actualiza_sin_guardar_mensaje(agente, monkeypatch, capsys):
    agente.messages = [{"role": "system", "content": "Sistema"}]
    agente.llm = Mock()
    agente._actualizar_resumen = Mock(return_value="Resumen generado")

    entrada = Mock(side_effect=["/resumir", "salir"])
    monkeypatch.setattr("builtins.input", entrada)

    agente.ejecutar()

    agente._actualizar_resumen.assert_called_once_with()
    agente.llm.responder.assert_not_called()
    agente.persistencia.guardar_mensaje.assert_not_called()
    assert agente.messages == [{"role": "system", "content": "Sistema"}]
    assert "Resumen actualizado." in capsys.readouterr().out

def test_consola_resumir_sin_pendientes_informa(agente, monkeypatch, capsys):
    agente.messages = [{"role": "system", "content": "Sistema"}]
    agente.llm = Mock()
    agente._actualizar_resumen = Mock(return_value=None)

    entrada = Mock(side_effect=["/resumir", "salir"])
    monkeypatch.setattr("builtins.input", entrada)


    agente.ejecutar()

    agente._actualizar_resumen.assert_called_once_with()
    assert "No hay mensajes antiguos pendientes de resumir." in capsys.readouterr().out