import json
import os
import sys
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
# DESCARGAR IMAGEN
# ============================================================

def descargar_imagen(nombre_archivo):
    os.makedirs(CARPETA_DESTINO, exist_ok=True)

    ruta_local = os.path.join(
        CARPETA_DESTINO,
        nombre_archivo
    )

    image_url = (
        f"https://raw.githubusercontent.com/"
        f"{GITHUB_REPOSITORY}/main/images/{nombre_archivo}"
    )

    print(f"Descargando imagen: {image_url}")

    try:
        response = requests.get(image_url, timeout=30)

        if response.status_code != 200:
            print(
                f"Error al descargar imagen. "
                f"HTTP {response.status_code}"
            )
            return None

        with open(ruta_local, "wb") as archivo:
            archivo.write(response.content)

        print(f"Imagen descargada: {ruta_local}")
        return ruta_local

    except Exception as e:
        print(f"Error descargando imagen: {e}")
        return None


# ============================================================
# SUBIR IMAGEN COMO BORRADOR
# ============================================================

def subir_imagen_borrador(ruta_imagen):
    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_VERSION}/{PAGE_ID}/photos"
    )

    payload = {
        "published": "false",
        "access_token": ACCESS_TOKEN
    }

    print(
        f"\nPaso 1: Subiendo imagen en borrador "
        f"({ruta_imagen})..."
    )

    try:
        with open(ruta_imagen, "rb") as imagen:
            response = requests.post(
                url,
                data=payload,
                files={"source": imagen},
                timeout=60
            )
    except Exception as e:
        print(f"Error subiendo imagen: {e}")
        return None

    print(
        f"Respuesta de Facebook "
        f"(HTTP {response.status_code}):"
    )
    print(response.text)

    if response.status_code != 200:
        return None

    try:
        data = response.json()
    except Exception:
        print("Facebook no devolvió JSON válido.")
        return None

    photo_id = data.get("id") or data.get("photo_id")

    if not photo_id:
        print("Facebook no devolvió un Photo ID válido.")
        return None

    print(f"Imagen subida con éxito. Photo ID: {photo_id}")
    return str(photo_id)


# ============================================================
# PUBLICAR IMAGEN + TEXTO
# ============================================================

def publicar_con_imagen(photo_id, mensaje):
    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_VERSION}/{PAGE_ID}/feed"
    )

    payload = {
        "message": mensaje,
        "attached_media": json.dumps([
            {"media_fbid": str(photo_id)}
        ]),
        "access_token": ACCESS_TOKEN
    }

    print("\nPaso 2: Publicando imagen y texto en el Feed...")
    print(f"Photo ID utilizado: {photo_id}")

    try:
        response = requests.post(
            url,
            data=payload,
            timeout=60
        )
    except Exception as e:
        print(f"Error publicando en Facebook: {e}")
        return None

    print(
        f"Respuesta de Facebook "
        f"(HTTP {response.status_code}):"
    )
    print(response.text)

    if response.status_code != 200:
        return None

    try:
        data = response.json()
    except Exception:
        print("Facebook no devolvió JSON válido.")
        return None

    post_id = data.get("id")

    if not post_id:
        print("Facebook no devolvió un ID de publicación.")
        return None

    print(f"¡Publicado con éxito! Post ID: {post_id}")
    return post_id


# ============================================================
# PUBLICAR SOLO TEXTO
# ============================================================

def publicar_solo_texto(mensaje):
    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_VERSION}/{PAGE_ID}/feed"
    )

    payload = {
        "message": mensaje,
        "access_token": ACCESS_TOKEN
    }

    print("\nPublicando publicación de solo texto...")

    try:
        response = requests.post(
            url,
            data=payload,
            timeout=60
        )
    except Exception as e:
        print(f"Error publicando en Facebook: {e}")
        return None

    print(
        f"Respuesta de Facebook "
        f"(HTTP {response.status_code}):"
    )
    print(response.text)

    if response.status_code != 200:
        return None

    try:
        data = response.json()
    except Exception:
        print("Facebook no devolvió JSON válido.")
        return None

    post_id = data.get("id")

    if not post_id:
        print("No se recibió ID de publicación.")
        return None

    print(f"¡Publicado con éxito! Post ID: {post_id}")
    return post_id


# ============================================================
# PROCESAR SIGUIENTE PUBLICACIÓN
# ============================================================

def publicar_siguiente():
    if not PAGE_ID or not ACCESS_TOKEN:
        print(
            "Error: faltan PAGE_ID o ACCESS_TOKEN "
            "en las variables de entorno."
        )
        sys.exit(1)

    if not os.path.exists(JSON_FILE):
        print(f"Error: no existe {JSON_FILE}.")
        sys.exit(1)

    try:
        with open(JSON_FILE, "r", encoding="utf-8") as archivo:
            publicaciones = json.load(archivo)
    except Exception as e:
        print(f"Error leyendo {JSON_FILE}: {e}")
        sys.exit(1)

    if not publicaciones:
        print("No hay publicaciones pendientes.")
        return

    # Tomamos la primera publicación, pero NO la eliminamos todavía.
    post = publicaciones[0]

    titulo = post.get("titulo", "")
    complemento = post.get("complemento", "")
    mensaje = post.get("mensaje", "")
    hashtags = post.get("hashtags", "")
    ruta_imagen_relativa = post.get("images", "")

    # Construir texto completo
    partes = [
        texto for texto in [
            titulo,
            complemento,
            mensaje,
            hashtags
        ]
        if texto
    ]

    texto_completo = "\n\n".join(partes)

    print("\n" + "=" * 60)
    print("PUBLICACIÓN")
    print("=" * 60)
    print(texto_completo)
    print("=" * 60)

    ruta_local_imagen = None
    post_id = None

    try:
        # ----------------------------------------------------
        # DESCARGAR IMAGEN
        # ----------------------------------------------------

        if ruta_imagen_relativa:
            nombre_archivo = os.path.basename(
                ruta_imagen_relativa
            )

            ruta_local_imagen = descargar_imagen(
                nombre_archivo
            )

            if not ruta_local_imagen:
                sys.exit(1)

        # ----------------------------------------------------
        # PUBLICAR
        # ----------------------------------------------------

        if ruta_local_imagen:
            photo_id = subir_imagen_borrador(
                ruta_local_imagen
            )

            if not photo_id:
                print("No se pudo subir la imagen.")
                sys.exit(1)

            post_id = publicar_con_imagen(
                photo_id,
                texto_completo
            )
        else:
            post_id = publicar_solo_texto(
                texto_completo
            )

        # ----------------------------------------------------
        # COMPROBAR RESULTADO
        # ----------------------------------------------------

        if not post_id:
            print(
                "\nLa publicación NO fue realizada."
            )
            print(
                "La publicación permanece en "
                "publicaciones.json para reintentar."
            )
            sys.exit(1)

        # ----------------------------------------------------
        # ELIMINAR DE LA COLA
        # ----------------------------------------------------

        publicaciones.pop(0)

        with open(
            JSON_FILE,
            "w",
            encoding="utf-8"
        ) as archivo:
            json.dump(
                publicaciones,
                archivo,
                ensure_ascii=False,
                indent=2
            )

        print(
            "\npublicaciones.json actualizado correctamente."
        )

    finally:
        # ----------------------------------------------------
        # ELIMINAR IMAGEN TEMPORAL
        # ----------------------------------------------------

        if (
            ruta_local_imagen
            and os.path.exists(ruta_local_imagen)
        ):
            try:
                os.remove(ruta_local_imagen)
                print(
                    f"Imagen temporal eliminada: "
                    f"{ruta_local_imagen}"
                )
            except Exception as e:
                print(
                    f"No se pudo eliminar la imagen temporal: {e}"
                )


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":
    publicar_siguiente()