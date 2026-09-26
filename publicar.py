import json
import os
import requests

PAGE_ID = os.environ.get("PAGE_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
GITHUB_REPOSITORY = os.environ.get(
    "GITHUB_REPOSITORY",
    "Javierfelixuts/aclama-a-Dios-auto-posts"
)

JSON_FILE = "publicaciones.json"
CARPETA_DESTINO = "images_ready_to_post"

# ============================================================
# PUBLICAR SIGUIENTE
# ============================================================

def publicar_siguiente():

    if not os.path.exists(JSON_FILE):
        print(f"El archivo {JSON_FILE} no existe.")
        return

    if not PAGE_ID or not ACCESS_TOKEN:
        print("Error: No se encontraron las variables de entorno PAGE_ID o ACCESS_TOKEN")
        return

    # --------------------------------------------------------
    # Leer publicaciones.json
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Construir el texto completo
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Descargar imagen desde GitHub
    # --------------------------------------------------------

    ruta_local_imagen = ""

    if ruta_imagen_relativa:

        nombre_archivo = os.path.basename(ruta_imagen_relativa)

        ruta_local_imagen = os.path.join(
            CARPETA_DESTINO,
            nombre_archivo
        )

        image_url = (
            f"https://raw.githubusercontent.com/"
            f"{GITHUB_REPOSITORY}/main/images/{nombre_archivo}"
        )

        print(f"Descargando imagen desde GitHub a: {ruta_local_imagen}")

        try:

            os.makedirs(CARPETA_DESTINO, exist_ok=True)

            img_response = requests.get(image_url)

            if img_response.status_code == 200:

                with open(ruta_local_imagen, "wb") as f_img:
                    f_img.write(img_response.content)

                print("Imagen descargada correctamente.")

            else:

                print(
                    f"Error al descargar la imagen "
                    f"(Código {img_response.status_code})"
                )

        except Exception as e:

            print(f"Excepción al descargar la imagen: {e}")

    tiene_imagen = bool(
        ruta_local_imagen and
        os.path.exists(ruta_local_imagen)
    )

    # ========================================================
    # PUBLICACIÓN
    # ========================================================

    try:

        # ====================================================
        # PASO 1: SUBIR IMAGEN COMO BORRADOR
        # ====================================================

        if tiene_imagen:

            print(
                f"Paso 1: Subiendo imagen en borrador "
                f"({ruta_local_imagen})..."
            )

            url_photo = (
                f"https://graph.facebook.com/v19.0/"
                f"{PAGE_ID}/photos"
            )

            payload_photo = {
                "published": "false",
                "access_token": ACCESS_TOKEN
            }

            with open(ruta_local_imagen, "rb") as img_file:

                res_photo = requests.post(
                    url_photo,
                    data=payload_photo,
                    files={
                        "source": img_file
                    }
                )

            if res_photo.status_code != 200:

                print(
                    "Error al subir la imagen a Facebook: "
                    f"{res_photo.text}"
                )

                exit(1)

            res_photo_data = res_photo.json()

            photo_id = (
                res_photo_data.get("id")
                or
                res_photo_data.get("photo_id")
            )

            print(
                f"Imagen subida con éxito. "
                f"Photo ID obtenido: {photo_id}"
            )

            if not photo_id:

                print(
                    "Error crítico: La API no devolvió "
                    "un ID de foto válido."
                )

                print(res_photo_data)

                exit(1)

            # =================================================
            # PASO 2: PUBLICAR EN EL FEED
            # =================================================

            print(
                "Paso 2: Publicando en el Feed "
                "utilizando attached_media..."
            )

            url_feed = (
                f"https://graph.facebook.com/v19.0/"
                f"{PAGE_ID}/feed"
            )

            payload_feed = {
                "message": texto_completo,
                "access_token": ACCESS_TOKEN,
                "published": "true",
                "attached_media": json.dumps([
                    {
                        "media_fbid": str(photo_id)
                    }
                ])
            }

            response = requests.post(
                url_feed,
                data=payload_feed
            )

        else:

            # =================================================
            # PUBLICACIÓN DE SOLO TEXTO
            # =================================================

            print(
                "Publicando post de solo texto "
                "directamente en el Feed..."
            )

            url_feed = (
                f"https://graph.facebook.com/v19.0/"
                f"{PAGE_ID}/feed"
            )

            payload_feed = {
                "message": texto_completo,
                "access_token": ACCESS_TOKEN,
                "published": "true"
            }

            response = requests.post(
                url_feed,
                data=payload_feed
            )

        # ====================================================
        # COMPROBAR PUBLICACIÓN DEL FEED
        # ====================================================

        if response.status_code == 200:

            res_data = response.json()

            feed_post_id = res_data.get("id")

            print(
                "¡Publicado en el muro con éxito!"
            )

            print(
                f"Post ID: {feed_post_id}"
            )

            # =================================================
            # PASO 3: CREAR HISTORIA DE FACEBOOK
            # =================================================
            #
            # Se intenta crear la historia solamente DESPUÉS
            # de que el Feed haya sido publicado correctamente.
            #
            # IMPORTANTE:
            # Esta parte utiliza el mismo PAGE_ID, TOKEN e imagen.
            #
            # =================================================

            if tiene_imagen:

                print("")
                print(
                    "Paso 3: Intentando crear "
                    "Historia de Facebook..."
                )

                url_story = (
                    f"https://graph.facebook.com/v19.0/"
                    f"{PAGE_ID}/stories"
                )

                payload_story = {
                    "access_token": ACCESS_TOKEN,
                    "photo_id": str(photo_id)
                }

                story_response = requests.post(
                    url_story,
                    data=payload_story
                )

                print(
                    f"Respuesta Historia: "
                    f"HTTP {story_response.status_code}"
                )

                print(
                    story_response.text
                )

                if story_response.status_code == 200:

                    story_data = story_response.json()

                    print(
                        "¡Historia creada correctamente!"
                    )

                    print(
                        f"Story ID: "
                        f"{story_data.get('id')}"
                    )

                else:

                    print(
                        "⚠️ El Feed se publicó correctamente, "
                        "pero la Historia NO pudo crearse."
                    )

                    print(
                        f"Facebook respondió: "
                        f"{story_response.text}"
                    )

            else:

                print(
                    "No se intentará crear Historia "
                    "porque esta publicación no tiene imagen."
                )

            # =================================================
            # GUARDAR JSON ACTUALIZADO
            # =================================================
            #
            # Se conserva tu comportamiento original:
            # una vez publicado correctamente el Feed,
            # se elimina de la cola.
            #
            # =================================================

            with open(
                JSON_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    publicaciones,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            print(
                f"Publicación eliminada de la cola "
                f"en {JSON_FILE}"
            )

        else:

            print(
                "Error al publicar en Facebook: "
                f"{response.text}"
            )

            exit(1)

    finally:

        # ====================================================
        # LIMPIEZA
        # ====================================================

        if (
            ruta_local_imagen
            and
            os.path.exists(ruta_local_imagen)
        ):

            os.remove(ruta_local_imagen)

            print(
                f"Imagen temporal eliminada de "
                f"{ruta_local_imagen}"
            )


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":
    publicar_siguiente()
