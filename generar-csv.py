import json
import pandas as pd

# Load the 100 items from the JSON file
with open("publicaciones.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# The user wants rows grouped into carousels/posts where each row represents a set of pages (P1 to P6)
# Let's check how many rows this creates (100 items / 6 items per row = approx 16-17 rows)
rows = []
for i in range(0, len(data), 6):
    chunk = data[i:i+6]
    if len(chunk) < 6:
        # Pad with the last or first items if needed to complete a row of 6 pages
        while len(chunk) < 6:
            chunk.append(data[0])
            
    # Parse elements for P1 to P6
    # P1: title + citation (split by last space or custom parsing, let's look at how original data was structured)
    # In chunk[0], title was like "Jehová es mi pastor; nada me faltará. Salmos 23:1"
    # Let's extract text and citation:
    t1 = chunk[0]["titulo"]
    # Usually the last part after space is citation if it contains numbers/colon or let's split intelligently
    parts = t1.rsplit(" ", 1)
    if len(parts) == 2 and any(char.isdigit() for char in parts[1]):
        p1_texto, p1_cita = parts[0], parts[1]
    else:
        p1_texto, p1_cita = t1, ""
        
    p2_texto = chunk[1]["titulo"]
    p3_texto = chunk[2]["titulo"]
    p3_cierre = "🤍 Compártelo en los comentarios. — Aclama a Dios"
    p4_texto = chunk[3]["titulo"]
    p5_texto = chunk[4]["titulo"]
    p6_texto = chunk[5]["titulo"]
    p6_cierre = "✍️ Escríbelo y compártelo con alguien que lo necesite. — Aclama a Dios"
    
    rows.append({
        "P1_Texto": p1_texto,
        "P1_Cita": p1_cita,
        "P2_Texto": p2_texto,
        "P3_Texto": p3_texto,
        "P3_Cierre": p3_cierre,
        "P4_Texto": p4_texto,
        "P5_Texto": p5_texto,
        "P6_Texto": p6_texto,
        "P6_Cierre": p6_cierre
    })

df_format = pd.DataFrame(rows)
df_format.to_csv("social_media_posts_carousel_format.csv", index=False, encoding="utf-8-sig")
print(f"Carousel CSV generated with {len(df_format)} rows.")