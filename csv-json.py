import pandas as pd
import json
import re

# Cargar el archivo CSV indicando explícitamente que está separado por tabuladores (sep='\t')
df = pd.read_csv("social_media_posts_carousel_format.csv", encoding="utf-8", sep='\t')

# Palabras comunes a ignorar para extraer hashtags significativos
stop_words = {
    "de", "la", "el", "en", "y", "a", "los", "las", "un", "una", "que", "es", 
    "por", "con", "su", "para", "como", "al", "lo", "sus", "le", "ha", "me", 
    "si", "sin", "sobre", "este", "ya", "cuando", "todo", "tu", "mi", "se", 
    "te", "o", "mas", "pero", "nos", "ni", "fue", "han", "hay", "esta", "estas", 
    "estos", "del", "qué", "quién", "cual", "cuales", "donde", "ello", "eso", 
    "esa", "ese", "esos", "esas", "otro", "otra", "otros", "otras"
}

def extract_hashtags(text):
    if not isinstance(text, str):
        return "#fe #Dios #esperanza #oracion #bendiciones #aclamaaDios"
        
    cleaned = re.sub("[¿?¡!,.;:\"'-]", "", text)
    words = cleaned.split()
    
    extracted = []
    for w in words:
        w_lower = w.lower()
        w_clean = re.sub(r'[^a-záéíóúñü]', '', w_lower)
        if len(w_clean) > 3 and w_clean not in stop_words:
            tag = f"#{w_clean}"
            if tag not in extracted:
                extracted.append(tag)
        if len(extracted) == 5:
            break
            
    defaults = ["#fe", "#Dios", "#esperanza", "#oracion", "#bendiciones"]
    for d in defaults:
        if len(extracted) < 5 and d not in extracted:
            extracted.append(d)
            
    extracted.append("#aclamaaDios")
    return " ".join(extracted)

json_list = []
img_counter = 121  # Cambia esto si necesitas empezar desde otro número (ej. 107)

for index, row in df.iterrows():
    p1_t = str(row.get('P1_Texto', '')).strip('"')
    p1_c = str(row.get('P1_Cita', '')).strip('"')
    p2_t = str(row.get('P2_Texto', '')).strip('"')
    p3_t = str(row.get('P3_Texto', '')).strip('"')
    p3_ci = str(row.get('P3_Cierre', '')).strip('"')
    p4_t = str(row.get('P4_Texto', '')).strip('"')
    p5_t = str(row.get('P5_Texto', '')).strip('"')
    p6_t = str(row.get('P6_Texto', '')).strip('"')
    p6_ci = str(row.get('P6_Cierre', '')).strip('"')

    items = [
        {
            "titulo": p1_t,
            "complemento": p1_c,
            "mensaje": f"La palabra de hoy nos recuerda una verdad eterna: {p1_t} Guía tu vida con esta promesa.",
            "hashtags": extract_hashtags(p1_t),
            "images": f"images/{img_counter}.png"
        },
        {
            "titulo": p2_t,
            "complemento": "",
            "mensaje": f"Un pensamiento para meditar hoy: {p2_t} Permite que la paz llene tu corazón.",
            "hashtags": extract_hashtags(p2_t),
            "images": f"images/{img_counter + 1}.png"
        },
        {
            "titulo": p3_t,
            "complemento": p3_ci,
            "mensaje": f"Queremos leerte: {p3_t} Escribe tu respuesta y edifiquémonos en comunidad.",
            "hashtags": extract_hashtags(p3_t),
            "images": f"images/{img_counter + 2}.png"
        },
        {
            "titulo": p4_t,
            "complemento": "",
            "mensaje": f"Elevemos juntos esta plegaria: {p4_t} Pon tus cargas en Sus manos.",
            "hashtags": extract_hashtags(p4_t),
            "images": f"images/{img_counter + 3}.png"
        },
        {
            "titulo": p5_t,
            "complemento": "",
            "mensaje": f"Declara con fuerza sobre tu vida: {p5_t} El favor divino te acompaña.",
            "hashtags": extract_hashtags(p5_t),
            "images": f"images/{img_counter + 4}.png"
        },
        {
            "titulo": p6_t,
            "complemento": p6_ci,
            "mensaje": f"Manifiesta tu fe hoy: {p6_t} Cree con todo tu corazón.",
            "hashtags": extract_hashtags(p6_t),
            "images": f"images/{img_counter + 5}.png"
        }
    ]

    for item in items:
        json_list.append(item)
    img_counter += 6

with open("posts_finales.json", "w", encoding="utf-8") as f:
    json.dump(json_list, f, ensure_ascii=False, indent=4)

print(f"¡Proceso completado con éxito! Se generaron {len(json_list)} registros en 'posts_finales.json'.")