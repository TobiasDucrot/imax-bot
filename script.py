import requests
from bs4 import BeautifulSoup
import os
import re

# --- CONFIGURACIÓN ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1531801696181817364/1RY9tM8yVrpK36N_k0EUCDfJ5mYbo10d0iQ9md7oFkodtrJ_3ngig1hdbCTwF_5u2Otd"
URL_SHOWCASE = "https://entradas.todoshowcase.com/showcase/pelicula?filmid=5875&house_id=3250"
ARCHIVO_ESTADO = "fechas_vistas.txt"
# ---------------------

def obtener_fechas():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        respuesta = requests.get(URL_SHOWCASE, headers=headers, timeout=15)
        
        if respuesta.status_code != 200:
            print(f"Error HTTP al intentar entrar: {respuesta.status_code}")
            return []
            
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        fechas_encontradas = []
        
        # Leemos TODO el texto visible de la página
        for texto in soup.stripped_strings:
            t = texto.strip()
            
            # Buscamos patrones de horario (ej. 22:30) o días (ej. Mie 12, 12/08)
            es_hora = re.search(r'\d{1,2}:\d{2}', t)
            es_fecha = re.search(r'\d{1,2}[/-]\d{1,2}', t)
            es_dia = re.search(r'(Lun|Mar|Mie|Mié|Jue|Vie|Sab|Sáb|Dom)\s*\d{1,2}', t, re.IGNORECASE)
            
            if (es_hora or es_fecha or es_dia) and len(t) < 20:
                fechas_encontradas.append(t)
                
        # Eliminamos duplicados manteniendo el orden
        fechas_unicas = list(dict.fromkeys(fechas_encontradas))
        
        # Esto imprime en el log lo que encontró para que podamos auditarlo
        print("🔍 Datos encontrados en la web:", fechas_unicas) 
        return fechas_unicas
        
    except Exception as e:
        print(f"Error al leer la web: {e}")
        return []

def main():
    fechas_actuales = obtener_fechas()
    if not fechas_actuales:
        print("No se encontraron fechas o la página está bloqueando la lectura directa.")
        return

    fechas_conocidas = []
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
            fechas_conocidas = f.read().splitlines()

    nuevas_fechas = [f for f in fechas_actuales if f not in fechas_conocidas]

    if nuevas_fechas:
        print(f"Nuevas funciones detectadas: {nuevas_fechas}")
        mensaje = "🚨 **¡NUEVAS FUNCIONES PARA LA ODISEA EN IMAX!** 🚨\n\nAgregaron horarios o fechas:\n"
        for nf in nuevas_fechas:
            mensaje += f"🍿 {nf}\n"
        mensaje += f"\nCorré a comprar: {URL_SHOWCASE}"
        
        requests.post(WEBHOOK_URL, json={"content": mensaje})

        with open(ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
            for fa in fechas_actuales:
                f.write(f"{fa}\n")
    else:
        print("Sin novedades. Las fechas y horarios son los mismos de antes.")

if __name__ == "__main__":
    main()
