import sqlite3
from pathlib import Path

from app.config import DATABASE_PATH, crear_directorios


class Persistencia:
    def __init__(self, db_path=None):
        if db_path is None:
            crear_directorios()
            self.db_path = DATABASE_PATH
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._crear_tablas()

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    def _crear_tablas(self):
        with self._conectar() as conexion:
            conexion.execute(
                """
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def guardar_mensaje(self, role, content):
        with self._conectar() as conexion:
            conexion.execute(
                """
                INSERT INTO mensajes (role, content)
                VALUES (?, ?)
                """,
                (role, content),
            )

    def cargar_mensajes(self):
        with self._conectar() as conexion:
            cursor = conexion.execute(
                """
                SELECT role, content
                FROM mensajes
                ORDER BY id ASC
                """
            )

            filas = cursor.fetchall()

        return [
            {
                "role": role,
                "content": content,
            }
            for role, content in filas
        ]

    def borrar_historial(self):
        with self._conectar() as conexion:
            conexion.execute(
                """
                DELETE FROM mensajes
                """
            )