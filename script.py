import os
import re
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURACIÓN ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1531801696181817364/1RY9tM8yVrpK36N_k0EUCDfJ5mYbo10d0iQ9md7oFkodtrJ_3ngig1hdbCTwF_5u2Otd"
URL_SHOWCASE = "https://entradas.todoshowcase.com/showcase/pelicula?filmid=5875&house_id=3250"
ARCHIVO_ESTADO = "fechas_vistas.txt"
# ---------------------

def obtener_fechas():
    # 1. Configuramos un Chrome "invisible"
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Modo oculto
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    try:
        # Instalamos y abrimos el navegador
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 2. Entramos a la página
        print("Entrando a Showcase y esperando 5 segundos a que cargue la web...")
        driver.get(URL_SHOWCASE)
        
        # 3. Esperamos 5 segundos reales a que el sitio dibuje las fechas
        time.sleep(5)
        
        # 4. Le sacamos una "foto" al código HTML ya cargado y cerramos Chrome
        html = driver.page_source
        driver.quit()
        
        # 5. Analizamos el texto de la página
        soup = BeautifulSoup(html, 'html.parser')
        fechas_encontradas = []
        
        for texto in soup.stripped_strings:
            t = texto.strip()
            # Buscamos horarios (ej. 22:30), fechas (12/08) o días (Mié 12)
            es_hora = re.search(r'\d{1,2}:\d{2}', t)
            es_fecha = re.search(r'\d{1,2}[/-]\d{1,2}', t)
            es_dia = re.search(r'(Lun|Mar|Mie|Mié|Jue|Vie|Sab|Sáb|Dom)\s*\d{1,2}', t, re.IGNORECASE)
            
            if (es_hora or es_fecha or es_dia) and len(t) < 30:
                fechas_encontradas.append(t)
                
        # Borramos duplicados
        fechas_unicas = list(dict.fromkeys(fechas_encontradas))
        print("🔍 Datos encontrados en la web:", fechas_unicas)
        return fechas_unicas
        
    except Exception as e:
        print(f"Error con el navegador virtual: {e}")
        return []

def main():
    fechas_actuales = obtener_fechas()
    if not fechas_actuales:
        print("No se encontraron fechas (sigue vacía o no hay funciones cargadas).")
        return

    fechas_conocidas = []
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
            fechas_conocidas = f.read().splitlines()

    nuevas_fechas = [f for f in fechas_actuales if f not in fechas_conocidas]

    if nuevas_fechas:
        print(f"Nuevas funciones detectadas: {nuevas_fechas}")
        mensaje = "🚨 **¡NUEVAS FUNCIONES PARA LA ODISEA EN IMAX!** 🚨\n\nEncontré estos datos en la web:\n"
        for nf in nuevas_fechas:
            mensaje += f"🍿 {nf}\n"
        mensaje += f"\nCorré a comprar: {URL_SHOWCASE}"
        
        requests.post(WEBHOOK_URL, json={"content": mensaje})

        # Guardamos todo para no avisar repetido la próxima vez
        with open(ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
            for fa in fechas_actuales:
                f.write(f"{fa}\n")
    else:
        print("Sin novedades. Las fechas y horarios son los mismos de antes.")

if __name__ == "__main__":
    main()
