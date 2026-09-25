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

    # ==========================================================
    # EXTRAER PRIMERA PUBLICACIÓN
    # ==========================================================

    post = publicaciones[0]

    titulo = post.get("titulo", "")
    complemento = post.get("complemento", "")
    mensaje = post.get("mensaje", "")
    hashtags = post.get("hashtags", "")
    ruta_imagen_relativa = post.get("images", "")

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

    print()
    print("==========================================")
    print("PUBLICACIÓN")
    print("==========================================")
    print(texto_completo)
    print("==========================================")
    print()

    # ==========================================================
    # DESCARGAR IMAGEN DESDE GITHUB
    # ==========================================================

    ruta_local_imagen = ""

    if ruta_imagen_relativa:

        nombre_archivo = os.path.basename(ruta_imagen_relativa)

        ruta_local_imagen = os.path.join(
            CARPETA_DESTINO,
            nombre_archivo
        )

        os.makedirs(
            CARPETA_DESTINO,
            exist_ok=True
        )

        image_url = (
            f"https://raw.githubusercontent.com/"
            f"{GITHUB_REPOSITORY}/main/images/{nombre_archivo}"
        )

        print(f"Descargando imagen:")
        print(image_url)

        try:

            img_response = requests.get(
                image_url,
                timeout=120
            )

            if img_response.status_code == 200:

                with open(
                    ruta_local_imagen,
                    "wb"
                ) as f_img:

                    f_img.write(img_response.content)

                print(
                    f"Imagen descargada: {ruta_local_imagen}"
                )

            else:

                print(
                    f"Error al descargar la imagen "
                    f"(Código {img_response.status_code})"
                )

                return

        except Exception as e:

            print(
                f"Excepción al descargar la imagen: {e}"
            )

            return

    # ==========================================================
    # PUBLICACIÓN
    # ==========================================================

    tiene_imagen = (
        bool(ruta_local_imagen)
        and os.path.exists(ruta_local_imagen)
    )

    try:

        if tiene_imagen:

            # --------------------------------------------------
            # PASO 1: SUBIR IMAGEN COMO BORRADOR
            # --------------------------------------------------

            print()
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

            with open(
                ruta_local_imagen,
                "rb"
            ) as img_file:

                res_photo = requests.post(
                    url_photo,
                    data=payload_photo,
                    files={
                        "source": img_file
                    },
                    timeout=120
                )

            print(
                f"Respuesta de Facebook "
                f"(HTTP {res_photo.status_code}):"
            )

            print(res_photo.text)

            if res_photo.status_code != 200:

                print(
                    f"Error al subir la imagen a Facebook: "
                    f"{res_photo.text}"
                )

                exit(1)

            photo_id = res_photo.json().get("id")

            print(
                f"Imagen subida con éxito. "
                f"Photo ID: {photo_id}"
            )

            if not photo_id:

                print(
                    "Error: Facebook no devolvió un Photo ID."
                )

                exit(1)

            # --------------------------------------------------
            # PASO 2: PUBLICAR EN EL FEED
            # --------------------------------------------------

            print()
            print(
                "Paso 2: Publicando directamente en el Feed..."
            )

            url_feed = (
                f"https://graph.facebook.com/v19.0/"
                f"{PAGE_ID}/feed"
            )

            payload_feed = {
                "message": texto_completo,
                "access_token": ACCESS_TOKEN,
                "published": "true",
                "attached_media": json.dumps(
                    [
                        {
                            "media_fbid": photo_id
                        }
                    ]
                )
            }

            print(
                f"Photo ID utilizado: {photo_id}"
            )

            response = requests.post(
                url_feed,
                data=payload_feed,
                timeout=120
            )

        else:

            # --------------------------------------------------
            # SOLO TEXTO
            # --------------------------------------------------

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
                data=payload_feed,
                timeout=120
            )

        # ======================================================
        # RESULTADO
        # ======================================================

        print()
        print(
            f"Respuesta final de Facebook "
            f"(HTTP {response.status_code}):"
        )

        print(response.text)

        if response.status_code == 200:

            res_data = response.json()

            print()
            print("==========================================")
            print("¡PUBLICADO CORRECTAMENTE!")
            print("==========================================")

            print(
                f"Post ID: {res_data.get('id')}"
            )

            # ----------------------------------------------
            # SOLO AHORA ELIMINAR DE LA COLA
            # ----------------------------------------------

            publicaciones.pop(0)

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
                "Publicación eliminada de publicaciones.json"
            )

        else:

            print()
            print("==========================================")
            print("ERROR AL PUBLICAR")
            print("==========================================")
            print(response.text)

            print()
            print(
                "La publicación permanece en "
                "publicaciones.json para reintentar."
            )

            exit(1)

    finally:

        # ======================================================
        # ELIMINAR IMAGEN TEMPORAL
        # ======================================================

        if (
            ruta_local_imagen
            and os.path.exists(ruta_local_imagen)
        ):

            os.remove(ruta_local_imagen)

            print(
                f"Imagen temporal eliminada: "
                f"{ruta_local_imagen}"
            )


if __name__ == "__main__":
    publicar_siguiente()