import sqlite3
from pathlib import Path
from contextlib import closing

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
        with closing(self._conectar()) as conexion, conexion:
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

            conexion.execute(
                """
                CREATE TABLE IF NOT EXISTS memoria (
                    clave TEXT PRIMARY KEY NOT NULL,
                    valor TEXT NOT NULL
                )
                """
            )

            conexion.execute(
                """
                CREATE TABLE IF NOT EXISTS resumen_conversacion(
                   id INTEGER PRIMARY KEY CHECK (id = 1),
                   contenido TEXT NOT NULL,
                   ultimo_mensaje_id INTEGER NOT NULL,
                   fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP 
                )
                """
            )

#Gestión de resumenes
    def guardar_resumen(self, contenido: str, ultimo_mensaje_id: int) -> None:
        with closing(self._conectar()) as conexion, conexion:
            conexion.execute(
                """
                INSERT INTO resumen_conversacion(
                    id,
                    contenido,
                    ultimo_mensaje_id
                )
                VALUES(1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    contenido = excluded.contenido,
                    ultimo_mensaje_id = excluded.ultimo_mensaje_id,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                """,
                (contenido, ultimo_mensaje_id)
            )


    def obtener_resumen(self):
        with closing(self._conectar()) as conexion, conexion:
            cursor = conexion.execute(
                """
                SELECT contenido, ultimo_mensaje_id FROM resumen_conversacion WHERE id = 1
                """
            )

            fila = cursor.fetchone()
            
            if fila is not None:
                return {"contenido": fila[0], "ultimo_mensaje_id": fila[1]}
            else: 
                return None


    def cargar_mensajes_para_resumen(self, despues_de_id: int,antes_de_id: int, limite: int):
        if despues_de_id < 0:
            raise ValueError("id negativo")
        elif limite < 0:
            raise ValueError("limite negativo")
        elif limite == 0:
            return []

        if antes_de_id <= 0:
            raise ValueError("id 0 o negativo")

        with closing(self._conectar()) as conexion:
            cursor = conexion.execute(
                """
                SELECT id, role, content FROM mensajes
                WHERE id > ? AND id < ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (despues_de_id, antes_de_id, limite)
            )

            filas = cursor.fetchall()

        return [
            {"id": id_mensaje, "role": role, "content": content}
            for id_mensaje, role, content in filas
        ]


    def obtener_id_inicio_historial_reciente(self, limite: int):
        if limite <= 0:
            raise ValueError("El límite debe ser positivo")

        with closing(self._conectar()) as conexion:
            cursor = conexion.execute(
                """
                SELECT ID FROM mensajes ORDER BY id DESC
                LIMIT 1 OFFSET ?
                """,
                (limite -1,)
            )
            filas = cursor.fetchone()

            if filas is None:
                return None
            else:
                return filas[0]

# Gestion de memoria
    
    #Guarda un dato o actualiza su valor si la clave existe
    def guardar_memoria(self, clave: str, valor: str):
        with closing(self._conectar()) as conexion, conexion:
            conexion.execute(
                """
                INSERT INTO memoria(clave, valor)
                VALUES (?, ?)
                ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor 
                """,
                (clave, valor)
            )

    def eliminar_memoria(self, clave: str) -> bool:
        with closing(self._conectar()) as conexion:
            with conexion:
                cursor = conexion.execute(
                    """
                    DELETE FROM memoria WHERE clave = ?
                    """,
                    (clave,)
                )

                return cursor.rowcount > 0


    def obtener_memoria(self, clave: str):
        with closing(self._conectar()) as conexion:
            cursor = conexion.execute(
                """
                SELECT valor FROM memoria WHERE clave = ?
                """,
                (clave,)
            )
            fila = cursor.fetchone()

            if fila is not None:
                return fila[0]
            return None  


    def cargar_memoria(self):
        with closing(self._conectar()) as conexion:
            cursor = conexion.execute(
                """
                SELECT clave, valor FROM memoria ORDER BY clave
                """
            )

            filas = cursor.fetchall()
            return dict(filas)


    def guardar_mensaje(self, role, content):
        with closing(self._conectar()) as conexion, conexion:
            conexion.execute(
                """
                INSERT INTO mensajes (role, content)
                VALUES (?, ?)
                """,
                (role, content)
            )

    def cargar_mensajes(self, limite = None):
        if limite is not None:
            if limite < 0:
                raise ValueError("El límite no puede ser negativo")
            if limite == 0:
                return []
            
        with closing(self._conectar()) as conexion:

            if limite is None:
                cursor = conexion.execute(
                    """
                    SELECT role, content
                    FROM mensajes
                    ORDER BY id ASC
                    """
                )
            else:
                cursor = conexion.execute(
                    """
                    SELECT role, content FROM mensajes
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limite,)
                )
                

            filas = cursor.fetchall()

            if limite is not None:
                filas.reverse()

        return [
            {
                "role": role,
                "content": content,
            }
            for role, content in filas
        ]


    def borrar_historial(self):
        with closing(self._conectar()) as conexion, conexion:
            conexion.execute(
                """
                DELETE FROM mensajes
                """
            )

