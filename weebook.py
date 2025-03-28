from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuración de la API de WhatsApp
VERIFY_TOKEN = "TU_TOKEN_VERIFICACION"
ACCESS_TOKEN = "EAAJoXxVG3sEBOZBIc0Ml36ZCbCnXIlwotx7QrtnZBzqn1o3hny72McjcI4hQWkrJb3RVKhwwvrYYC4i5XFNtyxRbDZBx4XKkmx7neWsf73v0thxYclLTkwgJCsELvq6CZCNpaP2xr6sukFTGOc4QmQASzuj6vsCPsdvMpX6WCkXwwPFJ2vkwmzhaKHzY0ZCxjGZAGZCEEGH3vQBg9z7Nc01CKUV6jGoZD"
PHONE_NUMBER_ID = "584419411425075"
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

@app.route("/", methods=["GET"])
def verificar_webhook():
    """ Verificación inicial del webhook en Meta Developer """
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    return challenge if token == VERIFY_TOKEN else ("Token inválido", 403)

@app.route("/", methods=["POST"])
def recibir_mensaje():
    """ Recibe mensajes de WhatsApp y responde automáticamente """
    data = request.get_json()
    guardar_log(data)

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                mensajes = change["value"].get("messages", [])
                if mensajes:
                    procesar_mensaje(mensajes[0])
    except Exception as e:
        print("Error procesando el mensaje:", e)

    return jsonify({"status": "success"}), 200

def guardar_log(data):
    """ Guarda los datos recibidos en un archivo de log """
    with open("log.json", "a") as f:
        f.write(str(data) + "\n")

def procesar_mensaje(mensaje):
    """ Procesa un mensaje recibido """
    telefono = mensaje["from"]
    if "text" in mensaje:
        texto = mensaje["text"]["body"].lower()
        print(f"Mensaje de {telefono}: {texto}")
        if verificar_contexto(telefono) == "problemas_pedido":
            reenviar_mensaje("5536609217", f"Problema reportado por {telefono}: {texto}")
            eliminar_contexto(telefono)
        else:
            responder_mensaje_con_opciones(telefono)
    elif "interactive" in mensaje:
        manejar_interactivo(mensaje["interactive"], telefono)

def manejar_interactivo(interactivo, telefono):
    """ Maneja las respuestas interactivas """
    if "button_reply" in interactivo:
        opcion_id = interactivo["button_reply"]["id"]
        print(f"Opción seleccionada por {telefono}: {opcion_id}")
        manejar_opcion(opcion_id, telefono)

def manejar_opcion(opcion_id, telefono):
    """ Maneja las opciones seleccionadas por el usuario """
    opciones = {
        "ver_catalogo": lambda: enviar_mensaje_interactivo(
            telefono,
            "¿Prefieres ver el catálogo en imágenes o visitar nuestra página oficial?",
            [{"id": "pagina_web", "title": "Página web"}, {"id": "imagenes", "title": "Imágenes"}]
        ),
        "pagina_web": lambda: responder_mensaje(
            telefono, "Antes de comprar, por favor crea una cuenta 📋🔑 \n https://www.relojescurrenmexico.com.mx/tienda/"
        ),
        "imagenes": lambda: responder_mensaje(
            telefono, "Aquí tienes nuestro catálogo en imágenes: https://tutienda.com/imagenes"
        ),
        "ayuda_pedido": lambda: enviar_mensaje_interactivo(
            telefono,
            "📦 ¿En qué podemos asistirte con tu pedido enviado? 😊",
            [{"id": "rastrear_pedido", "title": "Rastrear pedido"}, {"id": "problemas_pedido", "title": "Problemas con pedido"}]
        ),
        "info_empresa": lambda: enviar_mensaje_interactivo(
            telefono,
            "✨ Selecciona una opción para conocernos mejor:",
            [{"id": "ubicacion", "title": "Ubicación"}, {"id": "ser_proveedor", "title": "Ser proveedor"}]
        ),
        "ubicacion": lambda: enviar_mensaje_interactivo(
            telefono, 
            "🌟 Actualmente no tenemos una sucursal física, pero nuestro almacén está ubicado en la Ciudad de México. 🚚 Hacemos envíos a toda la República Mexicana y también ofrecemos envíos a contra entrega. ¡Estamos aquí para servirte! \n\n¿Prefieres ver el catálogo en imágenes o visitar nuestra página oficial?",
            [{"id": "pagina_web", "title": "Página web"}, {"id": "imagenes", "title": "Imágenes"}]
        ),
        "problemas_pedido": lambda: (
            responder_mensaje(telefono, "📦✨ ¿Podrías describir exactamente qué ocurrió con tu pedido? 😊"),
            guardar_contexto(telefono, "problemas_pedido")
        )
    }
    if opcion_id in opciones:
        opciones[opcion_id]()

def responder_mensaje(telefono, mensaje):
    """ Envía un mensaje de texto por WhatsApp """
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "text": {"body": mensaje}
    }
    enviar_solicitud(payload)

def responder_mensaje_con_opciones(telefono):
    """ Envía un mensaje interactivo con opciones por WhatsApp """
    enviar_mensaje_interactivo(
        telefono,
        "Hola, soy Mr. Curren. 😊 ¿En qué puedo ayudarte hoy? Elige una opción:",
        [
            {"id": "ver_catalogo", "title": "Ver catálogo"},
            {"id": "ayuda_pedido", "title": "Ayuda pedido"},
            {"id": "info_empresa", "title": "Información empresa"}
        ]
    )

def enviar_mensaje_interactivo(telefono, texto, botones):
    """ Envía un mensaje interactivo con botones """
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": texto},
            "action": {"buttons": [{"type": "reply", "reply": btn} for btn in botones]}
        }
    }
    enviar_solicitud(payload)

def enviar_solicitud(payload):
    """ Envía una solicitud a la API de WhatsApp """
    try:
        response = requests.post(WHATSAPP_API_URL, headers=HEADERS, json=payload)
        print("Respuesta de la API:", response.json())
    except requests.RequestException as e:
        print("Error al enviar la solicitud:", e)

def reenviar_mensaje(destino, mensaje):
    """ Reenvía un mensaje a otro número """
    payload = {
        "messaging_product": "whatsapp",
        "to": destino,
        "text": {"body": mensaje}
    }
    enviar_solicitud(payload)

# Funciones para manejar el contexto del cliente
contextos = {}

def guardar_contexto(telefono, contexto):
    """ Guarda el contexto actual del cliente """
    contextos[telefono] = contexto

def verificar_contexto(telefono):
    """ Verifica el contexto actual del cliente """
    return contextos.get(telefono)

def eliminar_contexto(telefono):
    """ Elimina el contexto del cliente """
    if telefono in contextos:
        del contextos[telefono]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)