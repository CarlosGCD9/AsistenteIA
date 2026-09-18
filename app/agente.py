from app.config import ASSISTANT_NAME
from app.persistence.persistencia import Persistencia
from app.llm.router import get_llm_provider

class AgenteIA:
    def __init__(self):

        self.persistencia = Persistencia()

        self.llm = get_llm_provider()

        self.system_prompt = (
            f"Tu nombre es {ASSISTANT_NAME}."
            "Eres un asistente útil que habla español "
            "y eres muy conciso con tus respuestas."
        )

        self.messages = [{
            "role": "system",
            "content": self.system_prompt
        }]

        self._cargar_historial()

    def _cargar_historial(self):
        mensajes_guardados = self.persistencia.cargar_mensajes()
        self.messages.extend(mensajes_guardados)

    def responder(self, mensaje_usuario: str) -> str:
        mensaje = {
            "role": "user",
            "content": mensaje_usuario
        }

        self.messages.append(mensaje)
        self.persistencia.guardar_mensaje(
            mensaje["role"],
            mensaje["content"]
        )

        respuesta = self.llm.responder(self.messages)

        mensaje_asistente = {
            "role": "assistant",
            "content": respuesta
        }

        self.messages.append(mensaje_asistente)
        self.persistencia.guardar_mensaje(
            mensaje_asistente["role"],
            mensaje_asistente["content"]
        )

        return respuesta


    def enviar_mensaje(self, mensaje):
        mensaje_usuario = {
            "role": "user",
            "content": mensaje,
        }

        self.messages.append(mensaje_usuario)
        self.persistencia.guardar_mensaje("user", mensaje)

        respuesta = self.llm.responder(self.messages)

        mensaje_asistente = {
            "role": "assistant",
            "content": respuesta,
        }

        self.messages.append(mensaje_asistente)
        self.persistencia.guardar_mensaje("assistant", respuesta)

        return respuesta

    def ejecutar(self):
        print(f"{ASSISTANT_NAME} iniciado")
        print(
            f"Mensajes anteriores cargados: {len(self.messages) - 1}"
        )

        print("escribe 'salir' para terminar.\n")

        while True:
            user_input = input("Tú: ").strip()

            if not user_input:
                continue

            if user_input.lower() in (
                "salir",
                "exit",
                "adios",
                "agur"
            ):

                print("Agur!")
                break

            try:

                respuesta = self.enviar_mensaje(user_input)

                if respuesta:
                    print(f"{ASSISTANT_NAME}: {respuesta}\n")

            except Exception as e:

                print(f"Error: {e}")