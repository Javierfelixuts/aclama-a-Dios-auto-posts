import json
import os
import requests

PAGE_ID = os.environ.get("PAGE_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "Javierfelixuts/aclama-a-Dios-auto-posts")

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
    complemento = post.get("complemento", "")
    mensaje = post.get("mensaje", "")
    hashtags = post.get("hashtags", "")
    ruta_imagen_relativa = post.get("images", "")

    # Obtener el enlace público directo de la imagen en GitHub
    image_url = ""
    if ruta_imagen_relativa:
        nombre_archivo = os.path.basename(ruta_imagen_relativa)
        image_url = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/main/images/{nombre_archivo}"

    # Construir el texto completo integrando la URL de la imagen al final
    partes_texto = []
    if titulo:
        partes_texto.append(titulo)
    if complemento:
        partes_texto.append(complemento)
    if mensaje:
        partes_texto.append(mensaje)
    
    # Adjuntamos el enlace de la imagen directamente en el texto para que Facebook la renderice
    if image_url:
        partes_texto.append(image_url)

    if hashtags:
        partes_texto.append(hashtags)

    texto_completo = "\n\n".join(partes_texto)

    print("Publicando post con enlace directo en el Feed...")
    url_feed = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
    
    payload = {
        "message": texto_completo,
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(url_feed, data=payload)

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