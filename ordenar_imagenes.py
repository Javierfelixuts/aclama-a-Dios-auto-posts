import os
import re

##cambiar variable 

start_number = 901
def orden_natural(cadena):
  # Extrae bloques de números y texto para ordenarlos como enteros
  return [
      int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', cadena)
  ]


def continuar_secuencia(
    carpeta_origen, carpeta_destino, inicio=start_number, prefijo="leccion"
):
  extensiones_validas = ('.jpg', '.jpeg', '.png', '.webp')

  # Obtener los archivos
  archivos = [
      f
      for f in os.listdir(carpeta_origen)
      if f.lower().endswith(extensiones_validas)
  ]

  if not archivos:
    print(f"No se encontraron imágenes en '{carpeta_origen}'.")
    return

  # ORDENAMIENTO NATURAL: Corrige el salto de 1.png -> 10.png
  archivos.sort(key=orden_natural)

  # Crear la carpeta de destino si no existe
  os.makedirs(carpeta_destino, exist_ok=True)

  contador = inicio
  print(
      f"Moviendo y renombrando {len(archivos)} imágenes a '{carpeta_destino}'"
      f" desde el #{inicio}...\n"
  )

  for archivo in archivos:
    extension = os.path.splitext(archivo)[1].lower()
    nuevo_nombre = f"{prefijo}{contador}{extension}"

    ruta_antigua = os.path.join(carpeta_origen, archivo)
    ruta_nueva = os.path.join(carpeta_destino, nuevo_nombre)

    # Mueve y renombra
    os.rename(ruta_antigua, ruta_nueva)
    print(f" Renombrado: {archivo} ➡️ {nuevo_nombre}")

    contador += 1

  print(
      f"\n¡Listo! Las imágenes ahora van hasta la #{contador - 1} en"
      f" '{carpeta_destino}'."
  )


if __name__ == "__main__":
  CARPETA_NUEVAS = "images/carpeta ordenada/"
  CARPETA_FINAL = "images/"
  NUMERO_INICIAL = start_number
  PREFIJO = ""

  continuar_secuencia(
      CARPETA_NUEVAS, CARPETA_FINAL, inicio=NUMERO_INICIAL, prefijo=PREFIJO
  )