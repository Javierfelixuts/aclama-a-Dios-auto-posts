import json
import os
import requests


# ============================================================
# CONFIGURACIÓN
# ============================================================

PAGE_ID = os.environ.get("PAGE_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

GITHUB_REPOSITORY = os.environ.get(
    "GITHUB_REPOSITORY",
    "Javierfelixuts/aclama-a-Dios-auto-posts"
)

GRAPH_VERSION = "v26.0"

JSON_FILE = "publicaciones.json"
CARPETA_DESTINO = "images_ready_to_post"


# ============================================================
# PUBLICAR SIGUIENTE PUBLICACIÓN
# ============================================================

def publicar_siguiente():

    print("==========================================")
    print("   PUBLICADOR AUTOMÁTICO - ACLAMA A DIOS")
    print("==========================================")
    print()

    # --------------------------------------------------------
    # VERIFICAR VARIABLES
    # --------------------------------------------------------

    if not PAGE_ID:
        print("ERROR: No se encontró PAGE_ID.")
        exit(1)

    if not ACCESS_TOKEN:
        print("ERROR: No se encontró ACCESS_TOKEN.")
        exit(1)

    if not os.path.exists(JSON_FILE):
        print(f"ERROR: El archivo {JSON_FILE} no existe.")
        exit(1)

    # --------------------------------------------------------
    # LEER PUBLICACIONES
    # --------------------------------------------------------

    try:

        with open(
            JSON_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            publicaciones = json.load(f)

    except Exception as e:

        print("ERROR leyendo publicaciones.json:")
        print(e)

        exit(1)

    # --------------------------------------------------------
    # COMPROBAR COLA
    # --------------------------------------------------------

    if not publicaciones:

        print("No hay publicaciones pendientes en la cola.")
        return

    # --------------------------------------------------------
    # TOMAR PRIMERA PUBLICACIÓN
    # --------------------------------------------------------

    post = publicaciones[0]

    titulo = post.get("titulo", "")
    complemento = post.get("complemento", "")
    mensaje = post.get("mensaje", "")
    hashtags = post.get("hashtags", "")
    ruta_imagen_relativa = post.get("images", "")

    # --------------------------------------------------------
    # CONSTRUIR TEXTO
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

    print("------------------------------------------")
    print("PUBLICACIÓN")
    print("------------------------------------------")
    print(texto_completo)
    print("------------------------------------------")
    print()

    # --------------------------------------------------------
    # PREPARAR CARPETA TEMPORAL
    # --------------------------------------------------------

    os.makedirs(
        CARPETA_DESTINO,
        exist_ok=True
    )

    ruta_local_imagen = ""

    # ========================================================
    # DESCARGAR IMAGEN
    # ========================================================

    if ruta_imagen_relativa:

        nombre_archivo = os.path.basename(
            ruta_imagen_relativa
        )

        ruta_local_imagen = os.path.join(
            CARPETA_DESTINO,
            nombre_archivo
        )

        image_url = (
            f"https://raw.githubusercontent.com/"
            f"{GITHUB_REPOSITORY}/main/images/"
            f"{nombre_archivo}"
        )

        print("Descargando imagen:")
        print(image_url)
        print()

        try:

            img_response = requests.get(
                image_url,
                timeout=120
            )

            if img_response.status_code != 200:

                print(
                    "ERROR al descargar la imagen."
                )

                print(
                    f"Código HTTP: "
                    f"{img_response.status_code}"
                )

                exit(1)

            with open(
                ruta_local_imagen,
                "wb"
            ) as f_img:

                f_img.write(
                    img_response.content
                )

            print(
                f"Imagen descargada: "
                f"{ruta_local_imagen}"
            )

            print()

        except requests.exceptions.RequestException as e:

            print(
                "ERROR de conexión descargando "
                "la imagen:"
            )

            print(e)

            exit(1)

    # ========================================================
    # PUBLICACIÓN
    # ========================================================

    try:

        # ====================================================
        # CASO CON IMAGEN
        # ====================================================

        if (
            ruta_local_imagen
            and os.path.exists(ruta_local_imagen)
        ):

            # ------------------------------------------------
            # PASO 1
            # SUBIR IMAGEN COMO BORRADOR
            # ------------------------------------------------

            print(
                f"Paso 1: Subiendo imagen en borrador "
                f"({ruta_local_imagen})..."
            )

            url_photo = (
                f"https://graph.facebook.com/"
                f"{GRAPH_VERSION}/"
                f"{PAGE_ID}/photos"
            )

            payload_photo = {
                "published": "false",
                "access_token": ACCESS_TOKEN
            }

            try:

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

            except requests.exceptions.RequestException as e:

                print()
                print(
                    "ERROR de conexión al subir "
                    "la imagen:"
                )

                print(e)

                exit(1)

            print(
                f"Respuesta de Facebook "
                f"(HTTP {res_photo.status_code}):"
            )

            print(res_photo.text)
            print()

            # ------------------------------------------------
            # COMPROBAR SUBIDA
            # ------------------------------------------------

            if res_photo.status_code != 200:

                print(
                    "ERROR: Facebook rechazó "
                    "la subida de la imagen."
                )

                exit(1)

            try:

                res_photo_data = res_photo.json()

            except Exception:

                print(
                    "ERROR: Facebook no devolvió "
                    "JSON válido al subir la imagen."
                )

                exit(1)

            photo_id = res_photo_data.get("id")

            print(
                f"Imagen subida con éxito. "
                f"Photo ID: {photo_id}"
            )

            print()

            if not photo_id:

                print(
                    "ERROR: Facebook no devolvió "
                    "un Photo ID válido."
                )

                exit(1)

            # ------------------------------------------------
            # PASO 2
            # PUBLICAR EN EL FEED
            # ------------------------------------------------

            print(
                "Paso 2: Publicando directamente "
                "en el Feed..."
            )

            url_feed = (
                f"https://graph.facebook.com/"
                f"{GRAPH_VERSION}/"
                f"{PAGE_ID}/feed"
            )

            # IMPORTANTE:
            # Construimos attached_media exactamente
            # como lo hicimos funcionar en Graph Explorer.
            attached_media = (
                f'[{{"media_fbid":"{photo_id}"}}]'
            )

            payload_feed = {
                "message": texto_completo,
                "access_token": ACCESS_TOKEN,
                "attached_media": attached_media
            }

            print(
                f"Photo ID utilizado: {photo_id}"
            )

            print(
                f"attached_media enviado: "
                f"{attached_media}"
            )

            print()

            try:

                response = requests.post(
                    url_feed,
                    data=payload_feed,
                    timeout=120
                )

            except requests.exceptions.RequestException as e:

                print()
                print(
                    "ERROR de conexión al publicar:"
                )

                print(e)

                exit(1)

        # ====================================================
        # CASO SOLO TEXTO
        # ====================================================

        else:

            print(
                "No hay imagen. "
                "Publicando post de solo texto..."
            )

            url_feed = (
                f"https://graph.facebook.com/"
                f"{GRAPH_VERSION}/"
                f"{PAGE_ID}/feed"
            )

            payload_feed = {
                "message": texto_completo,
                "access_token": ACCESS_TOKEN
            }

            try:

                response = requests.post(
                    url_feed,
                    data=payload_feed,
                    timeout=120
                )

            except requests.exceptions.RequestException as e:

                print()
                print(
                    "ERROR de conexión al publicar:"
                )

                print(e)

                exit(1)

        # ====================================================
        # RESULTADO FINAL
        # ====================================================

        print()
        print(
            f"Respuesta final de Facebook "
            f"(HTTP {response.status_code}):"
        )

        print(response.text)
        print()

        # ----------------------------------------------------
        # ÉXITO
        # ----------------------------------------------------

        if response.status_code == 200:

            try:

                res_data = response.json()

            except Exception:

                print(
                    "ERROR: Facebook respondió HTTP 200 "
                    "pero no devolvió JSON válido."
                )

                exit(1)

            post_id = res_data.get("id")

            print("==========================================")
            print("     ¡PUBLICADO CORRECTAMENTE!")
            print("==========================================")

            print(
                f"Post ID: {post_id}"
            )

            print()

            # ------------------------------------------------
            # ELIMINAR DE LA COLA
            # ------------------------------------------------

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
                "Publicación eliminada de "
                "publicaciones.json"
            )

            print()

        # ----------------------------------------------------
        # ERROR
        # ----------------------------------------------------

        else:

            print("==========================================")
            print("       ERROR AL PUBLICAR")
            print("==========================================")

            print(
                response.text
            )

            print()

            print(
                "La publicación permanece en "
                "publicaciones.json para reintentar."
            )

            exit(1)

    finally:

        # ====================================================
        # ELIMINAR IMAGEN TEMPORAL
        # ====================================================

        if (
            ruta_local_imagen
            and os.path.exists(ruta_local_imagen)
        ):

            try:

                os.remove(
                    ruta_local_imagen
                )

                print(
                    f"Imagen temporal eliminada: "
                    f"{ruta_local_imagen}"
                )

            except Exception as e:

                print(
                    "No se pudo eliminar la imagen "
                    "temporal:"
                )

                print(e)


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    publicar_siguiente()