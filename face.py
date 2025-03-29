import requests

ACCESS_TOKEN = "EAAJoXxVG3sEBO0u69XruVJqqwoZAWeQkZBUQUORmVtmscTziQJ2X9EPJZApGPS4vHe3G0JZA5ZA159nC9Aw5uXZBGvZAojuCtUC8fIu6CSvJizW5yoSMOdFo6EaT0iZBUZAEbNam6ZBOQEnrfSpvmkJ7ZBrY9PxsNoRWMyKhBUbApidzquhfKZA8ZBGifLb0LaCToWtzgtfd1UmVsxsZC1iWuNG7AT9g4ZAtHcZD"
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