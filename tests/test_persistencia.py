from app.persistence.persistencia import Persistencia

import pytest


def test_crear_base_de_datos(tmp_path):
    db_path = tmp_path / "test_memoria.db"

    Persistencia(db_path)

    assert db_path.exists()


def test_guardar_y_cargar_mensajes(tmp_path):
    db_path = tmp_path / "test_memoria.db"

    persistencia = Persistencia(db_path)

    persistencia.guardar_mensaje(
        "user",
        "Hola"
    )

    persistencia.guardar_mensaje(
        "assistant",
        "Hola, ¿qué tal?"
    )

    mensajes = persistencia.cargar_mensajes()

    assert mensajes == [
        {
            "role": "user",
            "content": "Hola"
        },
        {
            "role": "assistant",
            "content": "Hola, ¿qué tal?"
        }
    ]


def test_borrar_historial(tmp_path):
    db_path = tmp_path / "test_memoria.db"

    persistencia = Persistencia(db_path)

    persistencia.guardar_mensaje(
        "user",
        "Mensaje de prueba"
    )

    assert len(persistencia.cargar_mensajes()) == 1

    persistencia.borrar_historial()

    assert persistencia.cargar_mensajes() == []

def test_guardar_y_obtener_memoria(tmp_path):
    db_path = tmp_path / "test_memoria.db"

    persistencia = Persistencia(db_path)

    persistencia.guardar_memoria(
        "usuario",
        "Carlos"
    )

    assert persistencia.obtener_memoria("usuario") == "Carlos"

def test_actualizar_memoria(tmp_path):
    db_path = tmp_path / "test_memoria.db"

    persistencia = Persistencia(db_path)

    persistencia.guardar_memoria(
        "usuario",
        "Carlos"
    )

    persistencia.guardar_memoria(
        "usuario",
        "Luis"
    )

    assert persistencia.obtener_memoria("usuario") == "Luis"

def test_obtener_memoria_inexistente(tmp_path):
    db_path = tmp_path / "test_memoria.db"
    persistencia = Persistencia(db_path)

    assert persistencia.obtener_memoria("usuario") is None

def test_cargar_memoria_vacia(tmp_path):
    db_path = tmp_path / "test_memoria.db"

    persistencia = Persistencia(db_path)

    assert persistencia.cargar_memoria() == {}

def test_cargar_memoria(tmp_path):
    db_path = tmp_path / "test_memoria.db"
    persistencia = Persistencia(db_path)

    persistencia.guardar_memoria(
        "usuario",
        "Carlos"
    )

    persistencia.guardar_memoria(
        "idioma",
        "español"
    )

    pers = Persistencia(db_path)

    assert pers.cargar_memoria() == {
        "usuario": "Carlos",
        "idioma": "español",
    }

def test_eliminar_memoria_conserva_otros_recuerdos(tmp_path):
    persistencia = Persistencia(tmp_path / "test_memoria")

    persistencia.guardar_memoria(
        "usuario",
        "Carlos"
    )

    persistencia.guardar_memoria(
        "idioma",
        "español"
    )

    assert persistencia.eliminar_memoria("usuario") is True

    assert persistencia.obtener_memoria("usuario") is None

    assert persistencia.obtener_memoria("idioma") == "español"

def test_eliminar_memoria_inexistente(tmp_path):
    db_path = tmp_path / "test_memoria"
    persistencia = Persistencia(db_path)

    persistencia.guardar_memoria(
        "idioma",
        "español"
    )

    assert persistencia.eliminar_memoria("no existe") is False

    assert persistencia.cargar_memoria() == {"idioma": "español"}

def test_cargar_ultimos_mensajes(tmp_path):
    db_path = tmp_path / "test_memoria"
    persistencia = Persistencia(db_path)

    persistencia.guardar_mensaje(
        "user",
        "Mensaje 1"
    )

    persistencia.guardar_mensaje(
        "assistant",
        "Mensaje 2"
    )

    persistencia.guardar_mensaje(
        "user",
        "Mensaje 3"
    )

    persistencia.guardar_mensaje(
        "assistant",
        "Mensaje 4"
    )

    mensajes = persistencia.cargar_mensajes(limite=2)

    assert mensajes == [
        {"role": "user", "content": "Mensaje 3"},
        {"role": "assistant", "content": "Mensaje 4"},
    ]

def test_cargar_mensajes_con_limite_cero(tmp_path):
    db_path = tmp_path / "test_memoria"
    persistencia = Persistencia(db_path)

    persistencia.guardar_mensaje(
        "user",
        "prueba limite cero"
    )

    assert persistencia.cargar_mensajes(limite=0) == []

def test_cargar_mensajes_rechaza_limite_negativo(tmp_path):
    db_path = tmp_path / "test_memoria"
    persistencia = Persistencia(db_path)

    with pytest.raises(ValueError):
        persistencia.cargar_mensajes(limite=-1)