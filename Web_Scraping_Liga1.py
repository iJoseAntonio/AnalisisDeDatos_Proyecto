from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from unidecode import unidecode
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import pandas as pd
import time
import unicodedata
import queue

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

def obtener_equipos(temporada):

    """
    Obtiene la lista de equipos de la Liga 1 de Perú en una temporada específica.
    Parámetros:
        temporada: año de la temporada (ej. 2024 o 2025).
    Retorna:
        Lista de tuplas (nombre_equipo, url_equipo)
    """

    url = f"https://www.fotmob.com/es/leagues/131/overview/liga-1?season={temporada}"
    equipos = []
    try:
        print('Procesando equipos...')
        with webdriver.Chrome(options=options) as driver:
            driver.get(url)
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='TableRowCSS']"))
                )
            except Exception:
                print("No se encontraron equipos.")

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            filas_equipos = soup.select("div[class*='TableRowCSS'] div[class*='TableTeamCell'] a")
            
            for equipo in filas_equipos:
                nombre_tag = equipo.select_one("span.TeamName")
                nombre = nombre_tag.text.strip() if nombre_tag else "N/A"
                href = equipo.get("href")
                if href:
                    url_equipo = "https://www.fotmob.com" + href
                    equipos.append((nombre, url_equipo))
    except Exception as e:
        print(f"Error al cargar la página: {e}")

    equipos = sorted(set(equipos), key=lambda x: x[0])
    print(f"Equipos encontrados {temporada} : {len(equipos)}")
    return equipos

def obtener_partidos(liga, id, temporada):

    """
    Obtiene todos los partidos de la liga 1 de Perú para una temporada seleccionada.

    Parámetros:
        temporada: año de la temporada (ej. 2024 o 2025).
        delay: tiempo en segundos para esperar después de cargar cada página.

    Retorna:
        DataFrame con los partidos.
    """

    base_url = f"https://www.fotmob.com/es/leagues/{id}/matches/{liga}?season={temporada}&group=by-date&page="
    partidos_totales = []
    fechas_vistas = set()
    page = 0
    delay = 1

    with webdriver.Chrome(options=options) as driver:
        print(f"Procesando partidos...")
        while True:
            url = base_url + str(page)
            driver.get(url)
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "section[class*='LeagueMatchesSectionCSS']"))
                )
            except Exception:
                print("Advertencia: No se encontró la sección de partidos o la página tardó demasiado.")
                break

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            secciones = soup.select('section[class*="LeagueMatchesSectionCSS"]')

            if not secciones:
                print("Fin: no hay más páginas.")
                break

            nuevas_fechas = 0

            for seccion in secciones:
                fecha_tag = seccion.select_one('h3')
                fecha_texto = fecha_tag.text.strip() if fecha_tag else "N/A"
                if fecha_texto in fechas_vistas:
                    continue

                fechas_vistas.add(fecha_texto)
                nuevas_fechas += 1

                partidos = seccion.select('a[class*="MatchWrapper"]')
                for p in partidos:
                    try:
                        local = p.select_one('div[class*="StatusAndHomeTeamWrapper"] span[class*="TeamName"]').text.strip()
                        visitante = p.select_one('div[class*="AwayTeamAndFollowWrapper"] span[class*="TeamName"]').text.strip()
                        marcador_tag = p.select_one('span[class*="LSMatchStatusScore"]')
                        if marcador_tag:
                            marcador = marcador_tag.text.strip()
                        else:
                            hora_tag = p.select_one('span[class*="LSMatchStatusTime"] div[class*="TimeCSS"]')
                            if hora_tag:
                                marcador = hora_tag.text.strip()
                            else:
                                marcador = "Sin jugar"
 
                        href = p.get("href")
                        url_partido = "https://www.fotmob.com" + href if href else "N/A"

                        partidos_totales.append({
                            "fecha": fecha_texto,
                            "local": local,
                            "visitante": visitante,
                            "marcador": marcador,
                            "url": url_partido
                        })
                    except Exception as e:
                        print(f"Error procesando partido: {page} {e}")

            if nuevas_fechas == 0:
                print(f"Partidos completados {temporada}.")
                break

            page += 1
            if delay > 0:
                time.sleep(delay)

    df = pd.DataFrame(partidos_totales)
    df['fecha'] = df["fecha"].apply(_convertir_formato_fecha_DD_MM_YYYY)
    return df

def _convertir_formato_fecha_DD_MM_YYYY(fecha):
    meses = {
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
    }

    if isinstance(fecha, str):
        try:
            fecha_sin_tilde = unidecode(fecha.strip().lower())
            partes = fecha_sin_tilde.replace(',', '').split()

            if len(partes) >= 6:
                dia = partes[1]
                mes = meses.get(partes[3], '01')
                año = partes[5]
                return f"{dia.zfill(2)}-{mes}-{año}"
            elif len(partes) >= 4:
                dia = partes[1]
                mes = meses.get(partes[3], '01')
                año = '2025'  
                return f"{dia.zfill(2)}-{mes}-{año}"
            elif fecha_sin_tilde == 'ayer':
                ayer = datetime.now() - timedelta(days=1)
                return ayer.strftime("%d-%m-%Y")
            elif fecha_sin_tilde == 'hoy':
                hoy = datetime.now()
                return hoy.strftime("%d-%m-%Y")
            elif fecha_sin_tilde == 'manana':
                manana = datetime.now() + timedelta(days=1)
                return manana.strftime("%d-%m-%Y")

        except Exception as e:
            print(f"⚠️ Error en fecha: {fecha} -> {e}")
            return None
    return None

def _normalizar(texto):
    return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8').strip().lower()

def extraer_stats_partidos(df, max_workers=4):
    """
    Enriquecer un DataFrame de partidos con estadísticas de FotMob usando Selenium y multithreading.
    Parámetros:
        df: DataFrame con columna 'url'
        max_workers: número de workers para el scraping concurrente
    Retorna:
        El mismo DataFrame enriquecido con columnas de estadísticas
    """
    stats_base = [
        "Tiros totales", "Disparos a puerta", "Paradas del portero", "Pases", "Saques de esquina", "Faltas",
        "Tarjetas amarillas", "Tarjetas rojas"
    ]
    stats_objetivo = [_normalizar(s) for s in stats_base]

    for stat in stats_base:
        if f"{stat}_local" not in df.columns:
            df[f"{stat}_local"] = pd.NA
        if f"{stat}_visitante" not in df.columns:
            df[f"{stat}_visitante"] = pd.NA

    urls = df["url"].tolist()
    contador_errores = 0
    print(f"Procesando {len(urls)} partidos...")

    # Worker para scraping
    def worker(url_queue, results_list):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)

        nonlocal contador_errores

        while not url_queue.empty():
            try:
                idx, url = url_queue.get_nowait()
            except queue.Empty:
                break

            try:
                driver.get(url + ":tab=stats")
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Saques de esquina')]"))
                )
                time.sleep(1)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                stats = soup.find_all("li", class_=lambda c: c and "Stat" in c)

                resultados = {}
                for stat in stats:
                    titulo = stat.select_one("span.title")
                    if titulo:
                        nombre_stat = titulo.text.strip()
                        if _normalizar(nombre_stat) in stats_objetivo:
                            valores = stat.select("span[class*='StatValue']")
                            if len(valores) >= 2:
                                resultados[nombre_stat + "_local"] = valores[0].text.strip()
                                resultados[nombre_stat + "_visitante"] = valores[1].text.strip()

                if not resultados:
                    raise ValueError("No se encontraron estadísticas")

                results_list.append((idx, resultados))

            except Exception:
                contador_errores += 1
                results_list.append((idx, {}))
            finally:
                url_queue.task_done()

        driver.quit()

    # Crear y poblar la cola de URLs
    url_queue = queue.Queue()
    for i, url in enumerate(urls):
        url_queue.put((i, url))

    results_list = []

    total = url_queue.qsize()
    procesados = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker, url_queue, results_list) for _ in range(max_workers)]
        while not url_queue.empty():
            procesados = total - url_queue.qsize()
            print(f"Partidos procesados: {procesados}/{total}", end="\r")
            time.sleep(1)

    # Procesar resultados
    results_list.sort(key=lambda x: x[0])
    for idx, stats in results_list:
        for col, val in stats.items():
            df.at[idx, col] = val

    if contador_errores >=1 : print(f"Cantidad de partidos que no tienen estadisticas completas: {contador_errores}")
    print("Proceso finalizado.")
    return df