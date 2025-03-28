import requests

ACCESS_TOKEN = "EAAJoXxVG3sEBO7n7kTw0J3wGeEN1wx5sT0wCr7Wo56Y95IXag6ZAi3feIOV7vZBXOgZB4JHfandacul4VQZBxkmZAfG8IT5cK9bLWoRSjZAtA9Wl4vouixg8Dgllao6P99T8kSd02SZBsSrAhmiqePGZBUEbeXTuJDutUoFsazyPh8pH7pZB0N375y9O8MEJX6sIRtuwLYWNln55ySd4wlIurIdGM1v4ZD"
PHONE_NUMBER_ID = "584419411425075"
NUMERO_DESTINO = "525536609217"  # Sin el prefijo '+' para cumplir con el formato de la API

url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
data = {
    "messaging_product": "whatsapp",
    "to": NUMERO_DESTINO,
    "type": "template",
    "template": {
        "name": "hello_world",  # Nombre de la plantilla aprobada
        "language": {"code": "en_US"}  # Idioma de la plantilla
    }
}

response = requests.post(url, json=data, headers=headers)
print(response.json())