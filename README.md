# 📊 Web Scraping y Análisis de Datos de la Liga 1 (2024-2025)

Este proyecto extrae, procesa y analiza datos estadísticos de la Liga 1 de fútbol de Perú para la temporada 2024-2025. El objetivo es recopilar información de partidos, equipos y jugadores para realizar un análisis exploratorio.

## 📋 Características

-   **Web Scraping**: Script para extraer datos actualizados de la tabla de posiciones y resultados.
-   **Almacenamiento de Datos**: La información se guarda en un archivo `.xlsx` para facilitar su manejo.
-   **Análisis Exploratorio**: Un Jupyter Notebook para visualizar y analizar las estadísticas recopiladas.
-   **Visualización**: Dashboard interactivo en Power BI.

## 🚀 Instalación

Sigue estos pasos para configurar el entorno y ejecutar el proyecto.

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/tu-repositorio.git
    cd tu-repositorio
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    # Crear el entorno
    python -m venv venv

    # Activar en Windows
    .\venv\Scripts\activate

    # Activar en macOS/Linux
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Uso

1.  **Ejecutar el Web Scraper**:
    Para poblar o actualizar el archivo `Liga1_2024_2025.xlsx` con los últimos datos, ejecuta el siguiente script:
    ```bash
    python Web_Scraping_Liga1.py
    ```

2.  **Ver el Análisis de Datos**:
    Para explorar el análisis, abre y ejecuta el notebook `Analisis_Liga1_2024_2025.ipynb` usando Jupyter Notebook o Jupyter Lab.

## 📊 Dashboard en Power BI

A continuación se muestra una vista previa del dashboard creado en Power BI, que visualiza los datos recopilados en este proyecto.

*(Para mostrar tu imagen: súbela a tu repositorio de GitHub y reemplaza `ruta/a/tu/imagen.png` con el enlace directo al archivo)*

![Dashboard de Power BI](ruta/a/tu/imagen.png)

## 📂 Archivos del Proyecto

-   `Web_Scraping_Liga1.py`: Script principal que realiza el web scraping.
-   `Analisis_Liga1_2024_2025.ipynb`: Notebook con el análisis exploratorio de los datos.
-   `Liga1_2024_2025.xlsx`: Archivo Excel donde se almacenan los datos extraídos.
-   `requirements.txt`: Listado de las dependencias de Python necesarias.
