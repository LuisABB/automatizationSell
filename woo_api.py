import requests
import time

WC_API_URL = "https://www.relojescurrenmexico.com.mx/wp-json/wc/v3/products"
WC_CONSUMER_KEY = "ck_803245c4ae2633f53202fb14a0e331f6211ecda3"
WC_CONSUMER_SECRET = "cs_9f92afa473fba7fb04a9526b8e4aae8462f7697f"

def obtener_todos_los_productos():
    productos = []
    page = 1
    while True:
        params = {
            "consumer_key": WC_CONSUMER_KEY,
            "consumer_secret": WC_CONSUMER_SECRET,
            "per_page": 100,
            "page": page
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(WC_API_URL, params=params, headers=headers, timeout=60, verify=False)
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            productos.extend(data)
            page += 1
            time.sleep(1)  # Espera 1 segundo entre solicitudes
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            break
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
            break
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
            break
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred: {req_err}")
            break
    return productos

if __name__ == "__main__":
    productos = obtener_todos_los_productos()
    print(f"Se encontraron {len(productos)} productos en total.")

    # Filtrar productos con inventario mayor a 1
    productos_con_inventario = [p for p in productos if p.get('stock_quantity') and p['stock_quantity'] >= 1]

    print(f"Se encontraron {len(productos_con_inventario)} productos con inventario mayor a 1.")
    for p in productos_con_inventario:
        print(f"{p['id']} - {p['name']} - ${p['price']} - Stock: {p['stock_quantity']}")