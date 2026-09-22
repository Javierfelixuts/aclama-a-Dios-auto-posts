import os
import requests


PAGE_ID = "1222975510906733"
ACCESS_TOKEN = "EAAT7uwjEW68BSmXb5WbqZBbbj0qjRzZCEhut2AWAAhW9TWXTxtu04MyNCsb6vysju5ELXLC7stRn0tE5ZCjfrXYaqkeauahRTiUuLZBvEXy4YJZCLmivVyimfNi04OCiuOv9aUqQZB88eUvOhnBm6X5DHHE0395bt5vCAdZBe01NsKikn7zOuYpAtfCWB3q0x6lx5FYsDm6wtnKHOcRS1qgcSzfMFzB7sTFrZBu8CVsZD"  # Tu token largo

#PAGE_ID = os.environ.get("PAGE_ID_3")
#ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN_7")

# Consultar la información básica de la página (esto NO publica nada, solo lee)
url = f"https://graph.facebook.com/v19.0/{PAGE_ID}"
params = {
    "fields": "id,name,category",
    "access_token": ACCESS_TOKEN
}

try:
    response = requests.get(url, params=params)
    datos = response.json()

    print("--- VERIFICACIÓN DE CREDENCIALES DE FACEBOOK ---")

    # Si hay un error, Facebook lo incluirá en la respuesta
    if "error" in datos:
        print("❌ ¡Algo salió mal! Las credenciales o permisos no son correctos.")
        print(f"Detalle del error: {datos['error'].get('message')}")
    else:
        print("✅ ¡Todo correcto! Conexión exitosa.")
        print(f"Nombre de la página: {datos.get('name')}")
        print(f"ID de la página: {datos.get('id')}")
        print(f"Categoría: {datos.get('category')}")

except Exception as e:
    print(f"❌ Ocurrió un error de conexión: {e}")