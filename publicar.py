import os
import json
import requests
import tempfile

# ============================================================
# CONFIGURACIÓN
# ============================================================

GRAPH_VERSION = "v26.0"

PAGE_ID = os.environ.get("PAGE_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

JSON_URL = "https://raw.githubusercontent.com/TU_USUARIO/TU_REPOSITORIO/main/publicaciones.json"

# ============================================================
# VALIDACIONES
# ============================================================

if not PAGE_ID:
    raise Exception("❌ Falta la variable de entorno PAGE_ID")

if not ACCESS_TOKEN:
    raise Exception("❌ Falta la variable de entorno ACCESS_TOKEN")


# ============================================================
# COMPROBAR TOKEN DE FORMA SEGURA
# ============================================================

def comprobar_token():
    print("\n🔎 Comprobando token utilizado por GitHub...")

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/debug_token"

    params = {
        "input_token": ACCESS_TOKEN,
        "access_token": ACCESS_TOKEN
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=60
        )

        print(f"HTTP debug_token: {response.status_code}")

        data = response.json()

        if response.status_code != 200:
            print("⚠️ Facebook respondió con error al comprobar el token:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return False

        token_data = data.get("data", {})

        # IMPORTANTE:
        # Nunca mostramos el token.
        datos_seguros = {
            "is_valid": token_data.get("is_valid"),
            "app_id": token_data.get("app_id"),
            "application": token_data.get("application"),
            "type": token_data.get("type"),
            "profile_id": token_data.get("profile_id"),
            "user_id": token_data.get("user_id"),
            "expires_at": token_data.get("expires_at"),
            "data_access_expiration_time":
                token_data.get("data_access_expiration_time"),
            "scopes": token_data.get("scopes")
        }

        print(
            json.dumps(
                datos_seguros,
                indent=2,
                ensure_ascii=False
            )
        )

        return token_data.get("is_valid", False)

    except Exception as e:
        print(f"⚠️ Error comprobando token: {e}")
        return False


# ============================================================
# COMPROBAR PÁGINA
# ============================================================

def comprobar_pagina():

    print("\n🔎 Comprobando Página...")

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PAGE_ID}"

    params = {
        "fields": "id,name,can_post",
        "access_token": ACCESS_TOKEN
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=60
        )

        print(f"HTTP Página: {response.status_code}")

        data = response.json()

        if response.status_code != 200:
            print("❌ Error comprobando Página:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return False

        print(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False
            )
        )

        if str(data.get("id")) != str(PAGE_ID):
            print("❌ El PAGE_ID no coincide con la Página del token.")
            return False

        if data.get("can_post") is not True:
            print("⚠️ Facebook no indica can_post=true.")

        return True

    except Exception as e:
        print(f"❌ Error comprobando Página: {e}")
        return False


# ============================================================
# OBTENER PUBLICACIONES.JSON
# ============================================================

def obtener_publicaciones():

    print("\n📄 Descargando publicaciones.json...")

    try:
        response = requests.get(
            JSON_URL,
            timeout=60
        )

        response.raise_for_status()

        publicaciones = response.json()

        if not isinstance(publicaciones, list):
            raise Exception(
                "publicaciones.json no contiene una lista."
            )

        if len(publicaciones) == 0:
            print("ℹ️ No hay publicaciones pendientes.")
            return []

        print(
            f"✅ Publicaciones encontradas: {len(publicaciones)}"
        )

        return publicaciones

    except Exception as e:
        print(
            f"❌ Error descargando publicaciones.json: {e}"
        )
        raise


# ============================================================
# DESCARGAR IMAGEN
# ============================================================

def descargar_imagen(url_imagen):

    print("\n🖼️ Descargando imagen...")

    try:

        response = requests.get(
            url_imagen,
            timeout=120
        )

        response.raise_for_status()

        archivo_temp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".png"
        )

        archivo_temp.write(response.content)
        archivo_temp.close()

        print(
            f"✅ Imagen descargada: {archivo_temp.name}"
        )

        return archivo_temp.name

    except Exception as e:
        print(f"❌ Error descargando imagen: {e}")
        raise


# ============================================================
# SUBIR IMAGEN COMO BORRADOR
# ============================================================

def subir_imagen_borrador(ruta_imagen):

    print("\n==================================================")
    print("PASO 1: Subiendo imagen en borrador...")
    print("==================================================")

    url_photo = (
        f"https://graph.facebook.com/"
        f"{GRAPH_VERSION}/{PAGE_ID}/photos"
    )

    try:

        with open(ruta_imagen, "rb") as archivo:

            files = {
                "source": (
                    os.path.basename(ruta_imagen),
                    archivo,
                    "image/png"
                )
            }

            data = {
                "published": "false",
                "access_token": ACCESS_TOKEN
            }

            response = requests.post(
                url_photo,
                files=files,
                data=data,
                timeout=180
            )

        print(
            f"HTTP subida imagen: {response.status_code}"
        )

        resultado = response.json()

        print(
            json.dumps(
                resultado,
                indent=2,
                ensure_ascii=False
            )
        )

        if response.status_code != 200:
            raise Exception(
                "Facebook rechazó la subida de la imagen."
            )

        photo_id = resultado.get("id")

        if not photo_id:
            raise Exception(
                "Facebook no devolvió un Photo ID."
            )

        print(
            f"\n✅ Photo ID obtenido: {photo_id}"
        )

        return photo_id

    except Exception as e:
        print(
            f"❌ Error subiendo imagen: {e}"
        )
        raise


# ============================================================
# PUBLICAR EN FEED CON ATTACHED_MEDIA
# ============================================================

def publicar_en_feed(texto_completo, photo_id):

    print("\n==================================================")
    print("PASO 2: Publicando imagen + texto en el Feed...")
    print("==================================================")

    url_feed = (
        f"https://graph.facebook.com/"
        f"{GRAPH_VERSION}/{PAGE_ID}/feed"
    )

    # IMPORTANTE:
    # Lo mandamos exactamente como una cadena JSON.
    attached_media = json.dumps(
        [
            {
                "media_fbid": str(photo_id)
            }
        ],
        separators=(",", ":")
    )

    print(f"Photo ID utilizado: {photo_id}")
    print(
        f"attached_media enviado: {attached_media}"
    )

    payload_feed = {
        "message": texto_completo,
        "attached_media": attached_media,
        "access_token": ACCESS_TOKEN
    }

    try:

        response = requests.post(
            url_feed,
            data=payload_feed,
            timeout=180
        )

        print(
            f"\nHTTP publicación: {response.status_code}"
        )

        resultado = response.json()

        print(
            "Respuesta final de Facebook:"
        )

        print(
            json.dumps(
                resultado,
                indent=2,
                ensure_ascii=False
            )
        )

        if response.status_code != 200:
            raise Exception(
                "Facebook rechazó la publicación."
            )

        post_id = resultado.get("id")

        if not post_id:
            raise Exception(
                "Facebook no devolvió el ID de la publicación."
            )

        print(
            f"\n🎉 PUBLICACIÓN CREADA CORRECTAMENTE"
        )

        print(
            f"Post ID: {post_id}"
        )

        return post_id

    except Exception as e:

        print(
            f"\n❌ Error al publicar en Facebook: {e}"
        )

        raise


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("==============================================")
    print("🚀 PUBLICADOR FACEBOOK")
    print("==============================================")

    print(f"Graph API: {GRAPH_VERSION}")
    print(f"Page ID: {PAGE_ID}")

    # --------------------------------------------------------
    # 1. Comprobar token
    # --------------------------------------------------------

    token_valido = comprobar_token()

    if not token_valido:
        print(
            "\n⚠️ El token no pudo validarse correctamente."
        )
        print(
            "No continuamos para evitar publicar con "
            "credenciales incorrectas."
        )
        return

    # --------------------------------------------------------
    # 2. Comprobar Página
    # --------------------------------------------------------

    if not comprobar_pagina():
        print(
            "\n❌ La Página no pudo validarse."
        )
        return

    # --------------------------------------------------------
    # 3. Obtener publicaciones
    # --------------------------------------------------------

    publicaciones = obtener_publicaciones()

    if not publicaciones:
        return

    # --------------------------------------------------------
    # 4. Tomar primera publicación
    # --------------------------------------------------------

    publicacion = publicaciones[0]

    print("\n📝 Publicación seleccionada:")

    print(
        json.dumps(
            publicacion,
            indent=2,
            ensure_ascii=False
        )
    )

    # --------------------------------------------------------
    # 5. Construir texto
    # --------------------------------------------------------

    titulo = publicacion.get("titulo", "").strip()
    complemento = publicacion.get(
        "complemento",
        ""
    ).strip()
    mensaje = publicacion.get(
        "mensaje",
        ""
    ).strip()

    hashtags = publicacion.get(
        "hashtags",
        ""
    ).strip()

    partes = []

    if titulo:
        partes.append(titulo)

    if complemento:
        partes.append(complemento)

    if mensaje:
        partes.append(mensaje)

    if hashtags:
        partes.append(hashtags)

    texto_completo = "\n\n".join(partes)

    print("\n📢 Texto que será publicado:")
    print("----------------------------------------------")
    print(texto_completo)
    print("----------------------------------------------")

    # --------------------------------------------------------
    # 6. Obtener URL imagen
    # --------------------------------------------------------

    imagen_url = (
        publicacion.get("imagen")
        or publicacion.get("image")
        or publicacion.get("url_imagen")
        or publicacion.get("image_url")
    )

    if not imagen_url:
        raise Exception(
            "❌ La publicación no contiene URL de imagen."
        )

    print(
        f"\n🖼️ URL de imagen: {imagen_url}"
    )

    ruta_imagen = None

    try:

        # ----------------------------------------------------
        # 7. Descargar imagen
        # ----------------------------------------------------

        ruta_imagen = descargar_imagen(
            imagen_url
        )

        # ----------------------------------------------------
        # 8. Subir imagen como BORRADOR
        # ----------------------------------------------------

        photo_id = subir_imagen_borrador(
            ruta_imagen
        )

        # ----------------------------------------------------
        # 9. Publicar Feed + imagen
        # ----------------------------------------------------

        post_id = publicar_en_feed(
            texto_completo,
            photo_id
        )

        # ----------------------------------------------------
        # 10. Eliminar publicación del JSON
        # ----------------------------------------------------

        print(
            "\n💾 Publicación realizada correctamente."
        )

        publicaciones.pop(0)

        # IMPORTANTE:
        # Si tu JSON está en GitHub, este script solo puede
        # modificarlo localmente. GitHub Actions necesitará
        # posteriormente hacer commit/push si quieres guardar
        # el cambio en el repositorio.

        print(
            f"Publicaciones restantes: "
            f"{len(publicaciones)}"
        )

        print("\n✅ PROCESO TERMINADO.")

        return post_id

    finally:

        # ----------------------------------------------------
        # 11. Limpiar imagen temporal
        # ----------------------------------------------------

        if ruta_imagen and os.path.exists(ruta_imagen):

            try:
                os.remove(ruta_imagen)

                print(
                    "\n🧹 Imagen temporal eliminada."
                )

            except Exception as e:

                print(
                    f"⚠️ No se pudo eliminar "
                    f"la imagen temporal: {e}"
                )


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":
    main()