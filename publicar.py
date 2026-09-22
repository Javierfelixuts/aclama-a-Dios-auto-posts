import json
import os
import requests

PAGE_ID = os.environ.get("PAGE_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

JSON_FILE = "publicaciones.json"


def publicar_siguiente():
    if not os.path.exists(JSON_FILE):
        print(f"El archivo {JSON_FILE} no existe.")
        return

    if not PAGE_ID or not ACCESS_TOKEN:
        print("Error: No se encontraron las variables de entorno PAGE_ID o ACCESS_TOKEN.")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        publicaciones = json.load(f)

    if not publicaciones:
        print("No hay publicaciones pendientes en la cola.")
        return

    # Extraer el primer post de la cola (FIFO)
    post = publicaciones.pop(0)

    titulo = post.get("titulo", "")
    mensaje = post.get("mensaje", "")
    complemento = post.get("complemento", "")
    hashtags = post.get("hashtags", "")
    ruta_imagen = post.get("images", "")

    texto_completo = (
        f"📌 {titulo}\n\n"
        f"📝 {complemento}\n\n"
        f"💬 {mensaje}\n\n"
        f"{hashtags}"
    )

    tiene_imagen = bool(ruta_imagen and os.path.exists(ruta_imagen))

    if tiene_imagen:
        print(f"Publicando imagen con texto en Facebook ({ruta_imagen})...")
        url_api = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
        payload = {
            "caption": texto_completo,
            "access_token": ACCESS_TOKEN
        }

        with open(ruta_imagen, "rb") as img_file:
            response = requests.post(url_api, data=payload, files={"source": img_file})

    else:
        print("Publicando post de solo texto directamente en el Feed...")
        url_api = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
        payload = {
            "message": texto_completo,
            "access_token": ACCESS_TOKEN
        }
        response = requests.post(url_api, data=payload)

    if response.status_code == 200:
        res_data = response.json()
        print(f"¡Publicado en el muro con éxito! ID: {res_data.get('id')}")

        # Guardar el JSON actualizado sin la publicación procesada
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(publicaciones, f, ensure_ascii=False, indent=2)
    else:
        print(f"Error al publicar en Facebook: {response.text}")
        exit(1)


if __name__ == "__main__":
    publicar_siguiente()