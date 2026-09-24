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
    ruta_imagen_relativa = post.get("images", "")

    # Construir el texto completo
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

    # Obtener la URL de GitHub Raw de esa imagen específica
    image_url = ""
    if ruta_imagen_relativa:
        if ruta_imagen_relativa.startswith("http"):
            image_url = ruta_imagen_relativa
        else:
            ruta_limpia = ruta_imagen_relativa.lstrip("/")
            image_url = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/main/{ruta_limpia}"
        print(f"URL de imagen a descargar: {image_url}")

    temp_image_path = "temp_imagen.png"
    tiene_imagen = False

    # Descargar ÚNICAMENTE la imagen que toca
    if image_url:
        print("Descargando individualmente la imagen actual...")
        try:
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                with open(temp_image_path, "wb") as f_img:
                    f_img.write(img_response.content)
                tiene_imagen = True
            else:
                print(f"Error al descargar la imagen (Código {img_response.status_code})")
        except Exception as e:
            print(f"Excepción al descargar la imagen: {e}")

    # Publicar directamente en Facebook enviando el archivo binario y el texto juntos
    if tiene_imagen:
        print("Publicando imagen y texto directamente en un solo paso...")
        url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
        payload = {
            "message": texto_completo,
            "access_token": ACCESS_TOKEN
        }

        with open(temp_image_path, "rb") as img_file:
            response = requests.post(url, data=payload, files={"source": img_file})

        # Borrar inmediatamente la imagen temporal
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

    else:
        print("Publicando post de solo texto...")
        url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
        payload = {
            "message": texto_completo,
            "access_token": ACCESS_TOKEN
        }
        response = requests.post(url, data=payload)

    if response.status_code == 200:
        res_data = response.json()
        print(f"¡Publicado con éxito! ID: {res_data.get('id') or res_data.get('post_id')}")

        # Guardar el JSON actualizado sin la publicación procesada
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(publicaciones, f, ensure_ascii=False, indent=2)
    else:
        print(f"Error al publicar en Facebook: {response.text}")
        exit(1)

if __name__ == "__main__":
    publicar_siguiente()