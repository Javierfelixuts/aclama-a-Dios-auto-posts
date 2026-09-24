import json
import os
import requests

PAGE_ID = os.environ.get("PAGE_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "Javierfelixuts/aclama-a-Dios-auto-posts")

JSON_FILE = "publicaciones.json"
CARPETA_DESTINO = "images_ready_to_post"

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
    ruta_imagen_relativa = post.get("images", "") # Ej: "images/8.png" o "8.png"

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

    ruta_local_imagen = ""
    if ruta_imagen_relativa:
        # Extraer solo el nombre del archivo (ej. "8.png") para guardarlo en la carpeta existente
        nombre_archivo = os.path.basename(ruta_imagen_relativa)
        ruta_local_imagen = os.path.join(CARPETA_DESTINO, nombre_archivo)
        
        # Construir la URL de GitHub Raw desde donde se va a descargar el original
        image_url = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/main/images/{nombre_archivo}"
        
        print(f"Descargando imagen desde GitHub a: {ruta_local_imagen}")
        try:
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                with open(ruta_local_imagen, "wb") as f_img:
                    f_img.write(img_response.content)
            else:
                print(f"Error al descargar la imagen (Código {img_response.status_code})")
        except Exception as e:
            print(f"Excepción al descargar la imagen: {e}")

    # Verificar si la imagen se descargó correctamente en la carpeta existente
    tiene_imagen = bool(ruta_local_imagen and os.path.exists(ruta_local_imagen))

    try:
        if tiene_imagen:
            print("Publicando imagen y texto directamente en un solo paso...")
            url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
            payload = {
                "message": texto_completo,
                "access_token": ACCESS_TOKEN
            }

            # Leer la imagen desde la carpeta existente
            with open(ruta_local_imagen, "rb") as img_file:
                response = requests.post(url, data=payload, files={"source": img_file})
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

    finally:
        # Bloque de limpieza: borra únicamente la imagen descargada, la carpeta con su .gitkeep se queda intacta
        if ruta_local_imagen and os.path.exists(ruta_local_imagen):
            os.remove(ruta_local_imagen)
            print(f"Imagen temporal eliminada de {ruta_local_imagen}")

if __name__ == "__main__":
    publicar_siguiente()