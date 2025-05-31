from PIL import Image
import struct

def png_to_cur(png_path: str, cur_path: str, hotspot_x: int = 0, hotspot_y: int = 0):
    """
    Convierte un PNG a CUR usando un encabezado manual:
      - Escribe ICONDIR con wType=2 (cursor).
      - Escribe una sola ICONDIRENTRY con hotspot (X,Y) y luego adjunta los bytes PNG.
    """

    # 1) Abrimos el PNG y extraemos sus bytes
    img = Image.open(png_path)
    png_bytes = None
    with open(png_path, "rb") as f:
        png_bytes = f.read()

    # 2) Calculamos ancho/alto en un solo byte (max 255, si es 256 debe usarse 0)
    w, h = img.size
    bWidth  = w if w < 256 else 0
    bHeight = h if h < 256 else 0
    bColorCount = 0   # siempre 0 en un CUR moderno
    bReserved   = 0   # reservado
    # hotspot X,Y en WORD (2 bytes little-endian cada uno)
    # dwBytesInRes: longitud de los datos PNG
    png_size = len(png_bytes)
    # Offset: 6 bytes de ICONDIR + 16 bytes de ICONDIRENTRY = 22
    image_offset = 6 + 16

    # 3) Construimos el bloque ICONDIR (6 bytes):
    #    WORD idReserved (0), WORD idType (2 para CUR), WORD idCount (número de imágenes=1)
    icondir = struct.pack("<HHH", 0, 2, 1)

    # 4) Construimos la ICONDIRENTRY (16 bytes):
    #    BYTE  bWidth,
    #    BYTE  bHeight,
    #    BYTE  bColorCount,
    #    BYTE  bReserved,
    #    WORD  wHotspotX,
    #    WORD  wHotspotY,
    #    DWORD dwBytesInRes,
    #    DWORD dwImageOffset
    entry = struct.pack(
        "<BBBBHHI I",
        bWidth, bHeight, bColorCount, bReserved,
        hotspot_x, hotspot_y,
        png_size,
        image_offset
    )

    # 5) Escribimos todo en .cur: ICONDIR + ENTRY + datos PNG
    with open(cur_path, "wb") as outf:
        outf.write(icondir)
        outf.write(entry)
        outf.write(png_bytes)

    print(f"Generado cursor: {cur_path} (hotspot=({hotspot_x}, {hotspot_y}))")

if __name__ == "__main__":
    # Ajusta la ruta si tu PNG está en otra carpeta
    png_to_cur("imagenes/deco/cursor/stone_arrow_7.png", "stone_arrow.cur", hotspot_x=0, hotspot_y=0)
