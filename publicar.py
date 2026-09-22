import json
import os
import requests

PAGE_ID = os.environ.get("PAGE_ID_3")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN_7")

JSON_FILE = "publicaciones.json"


def publicar_siguiente():
    if not os.path.exists(JSON_FILE):
        print(f"El archivo {JSON_FILE} no existe.")
        return

    if not PAGE_ID or not ACCESS_TOKEN:
        print("Error: No se encontraron las variables de entorno PAGE_ID_3 o ACCESS_TOKEN_7.")
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
    desc_en = post.get("descripcion_ingles", "")
    desc_es = post.get("descripcion_espanol", "")
    hashtags = post.get("hashtags", "")
    ruta_imagen = post.get("images", "")

    texto_completo = (
        f"📌 {titulo}\n\n"
        f"💬 {mensaje}\n\n"
        f"🇬🇧 {desc_en}\n\n"
        f"🇪🇸 {desc_es}\n\n"
        f"{hashtags}"
    )

    tiene_imagen = bool(ruta_imagen and os.path.exists(ruta_imagen))

    if tiene_imagen:
        print(f"Paso 1: Subiendo imagen en borrador ({ruta_imagen})...")
        url_photo = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
        payload_photo = {
            "published": "false",
            "access_token": ACCESS_TOKEN
        }

        with open(ruta_imagen, "rb") as img_file:
            res_photo = requests.post(url_photo, data=payload_photo, files={"source": img_file})

        if res_photo.status_code != 200:
            print(f"Error al subir la imagen a Facebook: {res_photo.text}")
            exit(1)

        photo_id = res_photo.json().get("id")
        print(f"Imagen subida con éxito. Photo ID: {photo_id}")

        print("Paso 2: Publicando directamente en el Feed...")
        url_feed = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
        payload_feed = {
            "message": texto_completo,
            "access_token": ACCESS_TOKEN,
            "published": "true",
            "attached_media": json.dumps([{"media_fbid": photo_id}])
        }
        response = requests.post(url_feed, data=payload_feed)

    else:
        print("Publicando post de solo texto directamente en el Feed...")
        url_feed = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
        payload_feed = {
            "message": texto_completo,
            "access_token": ACCESS_TOKEN,
            "published": "true"
        }
        response = requests.post(url_feed, data=payload_feed)

    if response.status_code == 200:
        res_data = response.json()
        print(f"¡Publicado en el muro con éxito! Post ID: {res_data.get('id')}")

        # Guardar el JSON actualizado sin la publicación procesada
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(publicaciones, f, ensure_ascii=False, indent=2)
    else:
        print(f"Error al publicar en Facebook: {response.text}")
        exit(1)


if __name__ == "__main__":
    publicar_siguiente()