from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.persistence.persistencia import Persistencia

class AgenteIA:
    def __init__(self):

        self.client = OpenAI(
            api_key = OPENAI_API_KEY
        )

        self.persistencia = Persistencia()

        self.system_prompt = (
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

    def enviar_mensaje(self, mensaje):
        mensaje = mensaje.strip()

        if not mensaje:
            return None

        self.messages.append({
            "role": "user",
            "content": mensaje
        })

        self.persistencia.guardar_mensaje(
            "user",
            mensaje
        )

        response = self.client.responses.create(
            model = OPENAI_MODEL,
            input = self.messages
        )

        respuesta = response.output_text

        self.messages.append({
            "role": "assistant",
            "content": respuesta
        })

        self.persistencia.guardar_mensaje(
            "assistant",
            respuesta
        )

        return respuesta

    def ejecutar(self):
        print("Agente IA iniciado")
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
                    print(f"Asistente: {respuesta}\n")

            except Exception as e:

                print(f"Error: {e}")