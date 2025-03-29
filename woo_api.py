import requests
import time

WC_API_URL = "https://www.relojescurrenmexico.com.mx/wp-json/wc/v3/products"
WC_CONSUMER_KEY = "ck_803245c4ae2633f53202fb14a0e331f6211ecda3"
WC_CONSUMER_SECRET = "cs_9f92afa473fba7fb04a9526b8e4aae8462f7697f"

def obtener_todos_los_productos(type=None):
    """Obtiene todos los productos de WooCommerce, filtrados por categoría si se especifica."""
    productos = []
    page = 1
    while True:
        # Agregar el filtro de categoría si se proporciona un 'type'
        params = {
            "consumer_key": WC_CONSUMER_KEY,
            "consumer_secret": WC_CONSUMER_SECRET,
            "per_page": 100,
            "page": page
        }
        if type:
            params["category"] = type  # Filtrar por categoría (slug o id)

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

def mostrar_productos_con_inventario(type=None):
    """Obtiene y genera productos con inventario mayor a 1 uno por uno, incluyendo su imagen principal."""
    productos = obtener_todos_los_productos(type)

    # Filtrar productos con inventario mayor a 1
    productos_con_inventario = (p for p in productos if p.get('stock_quantity') and p['stock_quantity'] >= 1)

    for p in productos_con_inventario:
        # Obtener la URL de la imagen principal si existe
        imagen_principal = p['images'][0]['src'] if p.get('images') and len(p['images']) > 0 else "Sin imagen"
        # print(f"{p['id']} - {p['name']} - ${p['price']} - Stock: {p['stock_quantity']} - Imagen: {imagen_principal}")
        yield {
            "id": p['id'],
            "name": p['name'],
            "price": p['price'],
            "stock_quantity": p['stock_quantity'],
            "image": imagen_principal
        }

#17 hombre
#25 Dama
#18 Ofertas
#19 Cronografos

# if __name__ == "__main__":
#         total=0
#         for producto in mostrar_productos_con_inventario(17):
#             total += 1
#             print(f"Procesando producto: {producto['name']}")
#         print(f"Se procesaron {total} productos en total.")