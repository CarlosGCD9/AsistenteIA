from app.persistence.persistencia import Persistencia


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
