from flask import Flask, request, jsonify
from woo_api import mostrar_productos_con_inventario
import requests
import time
import urllib3


app = Flask(__name__)

# Configuración de la API de WhatsApp
VERIFY_TOKEN = "TU_TOKEN_VERIFICACION"
ACCESS_TOKEN = "EAAJoXxVG3sEBOxasOsOZBioErcwCoUWPOao5mPEnudBWwKZCYZBEDmc1dNz2LUeu6ZBSG7awSKWufkiqy5MilK3ed5u3OcIRp13yaklUB7N16fbFwHn7aK4MHw9sxIFs95G1vshRxoinBBaxiCDBjkvcuKZACH88ZCWktZAN8auZCDcY3ZAJ2dWkRw2gc1V7t2DAgAtEz0jMhJn45YiliuvyzcBbdfkcZD"
PHONE_NUMBER_ID = "584419411425075"
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        # Validar que el campo interactive contenga datos válidos
        if "list_reply" in mensaje["interactive"] or "button_reply" in mensaje["interactive"]:
            print(f"Interacción recibida de {telefono}: {mensaje['interactive']}")
            manejar_interactivo(mensaje["interactive"], telefono)
        else:
            print(f"\n\n->Interacción no válida recibida de {telefono}: {mensaje['interactive']}***********************************************\n\n")
    else:
        print(f"Mensaje no válido recibido de {telefono}: {mensaje}")

def manejar_interactivo(interactivo, telefono):
    """ Maneja las respuestas interactivas """
    if "list_reply" in interactivo:
        opcion_id = interactivo["list_reply"].get("id")
        if opcion_id:
            print(f"Opción seleccionada por {telefono}: {opcion_id}")
            manejar_opcion(opcion_id, telefono)  # Llama a manejar_opcion solo si es válido
        else:
            print(f"Interacción de lista no válida recibida de {telefono}: {interactivo}")
    elif "button_reply" in interactivo:
        opcion_id = interactivo["button_reply"].get("id")
        if opcion_id:
            print(f"Opción seleccionada por {telefono}: {opcion_id}")
            manejar_opcion(opcion_id, telefono)  # Llama a manejar_opcion solo si es válido
        else:
            print(f"Interacción de botón no válida recibida de {telefono}: {interactivo}")
    else:
        print(f"Interacción no válida recibida de {telefono}: {interactivo}")

def guardar_contexto(telefono, contexto):
    """ Guarda el contexto actual del cliente """
    contextos[telefono] = contexto

def manejar_opcion(opcion_id, telefono):
    """ Maneja las opciones seleccionadas por el usuario """
    # Verificar si ya hay una opción en proceso
    contexto_actual = verificar_contexto(telefono)
    if contexto_actual and contexto_actual != "completado":
        print(f"\t\t\n[Ya hay una opción en proceso para {telefono}: {contexto_actual}. Ignorando nueva solicitud...]\n")
        return

    # Guardar el contexto actual como la opción en proceso
    guardar_contexto(telefono, opcion_id)

    opciones = {
        "ver_catalogo": lambda: enviar_mensaje_interactivo(
            telefono,
            "¿Prefieres ver el catálogo en imágenes o visitar nuestra página oficial?",
            [{"id": "pagina_web", "title": "Página web"}, {"id": "imagenes", "title": "Imágenes"}]
        ),
        "pagina_web": lambda: responder_mensaje(
            telefono, "Antes de comprar, por favor crea una cuenta 📋🔑 \n https://www.relojescurrenmexico.com.mx/tienda/"
        ),
        "imagenes": lambda: tipo_catalogo(telefono),
        "hombre": lambda: productos_total(telefono, 17),
        "mujer": lambda: productos_total(telefono, 25),
        "ofertas": lambda: productos_total(telefono, 18),
        "todos": lambda: productos_total(telefono,None),
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

    # Validar si la opción seleccionada es válida
    if opcion_id in opciones:
        print("\n\n********************************************\n")
        print(f"Ejecutando opción seleccionada: {opcion_id}")
        print("********************************************\n\n")
        try:
            opciones[opcion_id]()  # Ejecutar la opción seleccionada
        finally:
            # Marcar el contexto como completado después de ejecutar la opción
            guardar_contexto(telefono, "completado")
    else:
        print(f"Opción no válida seleccionada: {opcion_id}")
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
        #print("Respuesta de la API:", response.json())
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
    print(f"Verificando contexto para {telefono}: {contextos.get(telefono)}")
    return contextos.get(telefono)

def eliminar_contexto(telefono):
    """ Elimina el contexto del cliente """
    if telefono in contextos:
        del contextos[telefono]

def tipo_catalogo(telefono):
    """ Envía un mensaje interactivo con opciones por WhatsApp """
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "🔍✨ Presiona VER OPCIONES y descubre los diferentes tipos de relojes que tenemos para ti. ¡Elige el que más te guste! ⌚🔥"},
            "action": {
                "button": "Ver opciones",
                "sections": [
                    {
                        "title": "Categorías",
                        "rows": [
                            {"id": "hombre", "title": "Hombre", "description": "Déjame ir por el catálogo de caballero, te aviso cuando termine ⏳😊"},
                            {"id": "mujer", "title": "Mujer", "description": "Déjame ir por el catálogo de dama, te aviso cuando termine ⏳😊"},
                            {"id": "ofertas", "title": "Ofertas", "description": "Déjame ir por el catálogo de ofertas, te aviso cuando termine ⏳😊"},
                            {"id": "todos", "title": "Todos", "description": "Déjame ir por todo el catálogo, te aviso cuando termine ⏳😊"}
                        ]
                    }
                ]
            }
        }
    }
    enviar_solicitud(payload)

def productos_total(telefono, tipo):
    """ Envía los productos disponibles al cliente en lotes con control de frecuencia """
    productos = list(mostrar_productos_con_inventario(tipo))  # Convertir el generador en una lista
    #print("Productos:", productos)
    print("Recuperando productos",tipo, "total:", len(productos))

    if productos:
        lote_tamano = 5  # Número de mensajes por lote
        tiempo_espera = 2  # Tiempo de espera entre lotes en segundos

        # Dividir los productos en lotes
        for i in range(0, len(productos), lote_tamano):
            lote = productos[i:i + lote_tamano]  # Obtener un lote de productos
            print(f"Enviando lote",i)

            for producto in lote:
                # Crear el payload para enviar el mensaje
                payload = {
                    "messaging_product": "whatsapp",
                    "to": telefono,
                    "type": "image",
                    "image": {
                        "link": producto['image'],  # URL de la imagen
                        "caption": f"Producto: {producto['name']}\nPrecio: ${producto['price']}"  # Subtítulo del mensaje
                    }
                }

                # Enviar el mensaje y verificar la respuesta
                if enviar_solicitud_y_verificar(payload):
                    print(f"Mensaje enviado correctamente para el producto: {producto['name']}")
                else:
                    print(f"Error al enviar el mensaje para el producto: {producto['name']}. Deteniendo el envío.")
                    return  # Detener el envío si ocurre un error

            # Esperar antes de enviar el siguiente lote
            print(f"Esperando {tiempo_espera} segundos antes de enviar el siguiente lote...")
            time.sleep(tiempo_espera)
    else:
        responder_mensaje(telefono, "No se encontraron productos disponibles.")

    print("Productos enviados al cliente:", len(productos))



def enviar_solicitud_y_verificar(payload):
    """ Envía una solicitud a la API de WhatsApp y verifica si fue exitosa """
    try:
        response = requests.post(WHATSAPP_API_URL, headers=HEADERS, json=payload)
        response_data = response.json()
        #print("Respuesta de la API:", response_data)

        # Verificar si la respuesta fue exitosa
        if response.status_code == 200 and "messages" in response_data:
            time.sleep(2)  # Esperar 10 segundos antes de intentar nuevamente
            return True  # Éxito
        elif response_data.get("error", {}).get("code") == 131056:
            print("Límite de mensajes alcanzado. Esperando antes de continuar...")
            time.sleep(10)  # Esperar 10 segundos antes de intentar nuevamente
            return False  # Fallo debido al límite de mensajes
        else:
            print("Error en la respuesta de la API:", response_data)
            return False  # Fallo por otro motivo
    except requests.RequestException as e:
        print("Error al enviar la solicitud:", e)
        return False  # Fallo

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)