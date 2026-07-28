import requests
from bs4 import BeautifulSoup
import os

# --- CONFIGURACIÓN ---
WEBHOOK_URL = "ACA_PEGA_TU_LINK_DE_DISCORD"
URL_SHOWCASE = "https://entradas.todoshowcase.com/showcase/pelicula?filmid=5875&house_id=3250"
ARCHIVO_ESTADO = "fechas_vistas.txt"
# ---------------------

def obtener_fechas():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        respuesta = requests.get(URL_SHOWCASE, headers=headers, timeout=10)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        fechas_encontradas = []
        
        # En la web de Showcase, las fechas suelen estar en menús desplegables (options) 
        # o botones. Extraemos los textos de las opciones disponibles.
        opciones = soup.find_all('option')
        for op in opciones:
            texto = op.text.strip()
            # Filtramos para quedarnos solo con lo que parezca una fecha (ej: contiene un número o mes)
            if any(char.isdigit() for char in texto) and len(texto) < 30:
                fechas_encontradas.append(texto)
                
        return list(dict.fromkeys(fechas_encontradas)) # Elimina duplicados
    except Exception as e:
        print(f"Error al leer la web: {e}")
        return []

def main():
    fechas_actuales = obtener_fechas()
    if not fechas_actuales:
        print("No se encontraron fechas o la estructura de la web cambió.")
        return

    # Leemos las fechas que el bot ya conoce
    fechas_conocidas = []
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
            fechas_conocidas = f.read().splitlines()

    # Buscamos cuáles son nuevas
    nuevas_fechas = [f for f in fechas_actuales if f not in fechas_conocidas]

    if nuevas_fechas:
        mensaje = "🚨 **¡NUEVAS FUNCIONES PARA LA ODISEA EN IMAX!** 🚨\n\nAgregaron:\n"
        for nf in nuevas_fechas:
            mensaje += f"🍿 {nf}\n"
        mensaje += f"\nCorré a comprar: {URL_SHOWCASE}"
        
        # Mandar a Discord
        requests.post(WEBHOOK_URL, json={"content": mensaje})

        # Guardar las nuevas fechas en el archivo para no volver a avisar por las mismas
        with open(ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
            for fa in fechas_actuales:
                f.write(f"{fa}\n")
    else:
        print("Sin novedades.")

if __name__ == "__main__":
    main()
