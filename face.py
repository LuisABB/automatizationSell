import requests

ACCESS_TOKEN = "EAAJoXxVG3sEBO0heZBQ7R8pU3sTXYPG94rQc1pZBeIluZClT24MdXjxfnMotT1dfWqBwsrVXPMNt2qcGedqyLMeZA2HX2GvgHCF5bboIannYzmgYWyl8YU39XA2LKkjY125AWyHFP7cyEnfSHDRu8Vg3dsOtUZAedG7ZB8pzZCi6x9ectOZCLZADK1bRtAT54PKMK3clOfzFUHeLlxlxZACikVJLvDdw0ZD"
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