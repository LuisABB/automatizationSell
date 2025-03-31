import requests

ACCESS_TOKEN = "EAAJoXxVG3sEBOxasOsOZBioErcwCoUWPOao5mPEnudBWwKZCYZBEDmc1dNz2LUeu6ZBSG7awSKWufkiqy5MilK3ed5u3OcIRp13yaklUB7N16fbFwHn7aK4MHw9sxIFs95G1vshRxoinBBaxiCDBjkvcuKZACH88ZCWktZAN8auZCDcY3ZAJ2dWkRw2gc1V7t2DAgAtEz0jMhJn45YiliuvyzcBbdfkcZD"
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