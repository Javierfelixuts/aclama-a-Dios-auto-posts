import json
import os
import requests

PAGE_ID = os.environ.get("PAGE_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
# GitHub provee automáticamente el nombre del repo (ej. "tu-usuario/tu-repo")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "tu-usuario/tu-repo")

JSON_FILE = "publicaciones.json"

def publicar_siguiente():
    if not os.path.exists(JSON_FILE):
        print(f"El archivo {JSON_FILE} no existe.")
        return

    if not PAGE_ID or not ACCESS_TOKEN:
        print("Error: No se encontraron las variables de entorno PAGE_ID o ACCESS_TOKEN")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        publicaciones = json.load(f)

    if not publicaciones:
        print("No hay publicaciones pendientes en la cola.")
        return

    # Extraer el primer post de la cola (FIFO)
    post = publicaciones.pop(0)

    titulo = post.get("titulo", "")
    complemento = post.get("complemento", "")
    mensaje = post.get("mensaje", "")
    hashtags = post.get("hashtags", "")
    ruta_imagen_relativa = post.get("images", "")  # Ej: "images/6.png"

    # Construir el texto adaptado
    partes_texto = []
    if titulo:
        partes_texto.append(titulo)
    if complemento:
        partes_texto.append(complemento)
    if mensaje:
        partes_texto.append(mensaje)
    if hashtags:
        partes_texto.append(hashtags)

    texto_completo = "\n\n".join(partes_texto)

    # Si hay una ruta de imagen, construimos su URL pública de GitHub Raw
    image_url = ""
    if ruta_imagen_relativa:
        # Quitamos la barra inicial si la tuviera para evitar doble barra //
        ruta_limpia = ruta_imagen_relativa.lstrip("/")
        image_url = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/main/{ruta_limpia}"
        print(f"URL de imagen generada: {image_url}")

    if image_url:
        print("Paso 1: Subiendo imagen a Facebook mediante URL...")
        url_photo = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
        payload_photo = {
            "published": "false",
            "url": image_url,  # <-- AQUÍ ESTÁ EL TRUCO: Pasamos la URL en lugar de abrir el archivo binario
            "access_token": ACCESS_TOKEN
        }

        res_photo = requests.post(url_photo, data=payload_photo)

        if res_photo.status_code != 200:
            print(f"Error al subir la imagen a Facebook: {res_photo.text}")
            exit(1)

        photo_id = res_photo.json().get("id")
        print(f"Imagen subida con éxito. Photo ID: {photo_id}")

        print("Paso 2: Publicando en el Feed con imagen adjunta...")
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