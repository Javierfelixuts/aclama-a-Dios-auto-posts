def publicar_story(imagen, payload_photo, page_id, graph_api_url):
    """
    Publica una imagen como historia de Facebook.
    imagen: archivo abierto en modo binario.
    payload_photo: parámetros que ya utilizas para subir fotos.
    page_id: ID de tu página.
    graph_api_url: por ejemplo, https://graph.facebook.com/v26.0
    """
    try:
        # 1. Subir la imagen sin publicarla en el feed
        response = requests.post(
            f"{graph_api_url}/{page_id}/photos",
            data=payload_photo,
            files={"source": imagen},
            timeout=60,
        )
        response.raise_for_status()

        photo_id = response.json().get("id")
        if not photo_id:
            print("❌ No se recibió el ID de la foto.")
            return False

        # 2. Crear la historia con la foto subida
        payload_story = {
            "photo_id": photo_id,
            "access_token": payload_photo["access_token"],
        }

        response = requests.post(
            f"{graph_api_url}/{page_id}/photo_stories",
            data=payload_story,
            timeout=60,
        )
        response.raise_for_status()

        print("✅ Historia publicada correctamente.")
        return True

    except requests.RequestException as error:
        detalle = (
            error.response.text
            if error.response is not None
            else str(error)
        )
        print(f"❌ Error al publicar la historia: {detalle}")
        return False