from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import requests
import os
import re

web = "https://classic-football-fhirts052.x.yupoo.com/collections/4124114"
path = "C:/Users/PC/OneDrive/Documentos/chromedriver-win64/chromedriver.exe"
service = Service(executable_path=path)
driver = webdriver.Chrome(service=service)

nombre_carpeta = "shorts-football"
nombres_no_descargados = list()

# Abrir la página web
driver.get(web)

# Esperar a que la página cargue completamente
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'album__main')]")))

# Obtener cookies de Selenium
cookies = driver.get_cookies()

# Usar una sesión de requests para mantener las cookies
session = requests.Session()

# Añadir cookies a la sesión
for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])

# Añadir headers a la solicitud para simular un navegador real
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
    'Referer': web
}

# Obtener todos los álbumes disponibles
albums = WebDriverWait(driver, 5).until(
    EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'album__main')]"))
)

# Iterar sobre cada álbum
for i in range(len(albums)):
    try:
        # Hacer clic en el álbum
        albums[i].click()

        # Copiar el nombre de la imagen
        copiar_nombre = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'showalbumheader__gallerytitle')]"))
        )
        nombre_obtenido = copiar_nombre.text

        # Sanitizar el nombre del archivo para evitar caracteres no válidos
        nombre_obtenido = re.sub(r'[<>:"/\\|?*]', '', nombre_obtenido)

        # Hacer las imágenes grandes
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@data-tab,'max')]"))).click()
    
        # Esperar a que las imágenes se carguen
        try:
         # Intentar con el primer XPATH
            imagenes = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//img[contains(@class,'autocover image__img image__portrait')]")))

        except TimeoutException:
            print("Primer XPATH no encontró imágenes, intentando con el segundo XPATH...")
            # Intentar con el segundo XPATH (corregido)
            imagenes = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//img[contains(@class,'autocover image__img image__portrait') or contains(@class,'autocover image__img image__landscape')]")))


        # Depurar el contenido de las imágenes
        print(f"Cantidad de imágenes encontradas en el álbum '{nombre_obtenido}': {len(imagenes)}")

        
        url_imagen = imagenes[-1].get_attribute('data-origin-src')
        print(f"URL de la imagen: {url_imagen}")

        if url_imagen:
            # Asegurarse de que el URL tenga el esquema completo
            if url_imagen.startswith('//'):
                url_imagen = 'https:' + url_imagen

            # Descargar la imagen usando la sesión
            img_data = requests.get(url_imagen, headers=headers).content

            # Crear carpeta de descarga
            ruta = f"C:/Users/PC/OneDrive/Escritorio/fotos-jerseys-python/{nombre_carpeta}"
            os.makedirs(ruta, exist_ok=True)

            # Crear el nombre del archivo con su ruta completa
            nombre_archivo = os.path.join(ruta, f"{nombre_obtenido}.jpg")  # Nombre único por álbum y número de imagen

            # Guardar la imagen en la carpeta
            with open(nombre_archivo, "wb") as handler:
                handler.write(img_data)

            print(f"Imagen guardada en {nombre_archivo}")
        else:
            print("No se pudo obtener el URL de la imagen.")
            
        
        # Regresar a la página principal después de descargar todas las imágenes
        driver.back()

        # Esperar a que la página principal se cargue de nuevo
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'album__main')]")))

        # Volver a obtener la lista de álbumes después de regresar
        albums = driver.find_elements(By.XPATH, "//a[contains(@class, 'album__main')]")

    except Exception as e:
        print(f"Ocurrió un error con el álbum {nombre_obtenido if 'nombre_obtenido' in locals() else i}: {e}")
        if 'nombre_obtenido' in locals():
            nombres_no_descargados.append(nombre_obtenido)
        driver.get(web)
        # Regresar a la página principal en caso de error
        driver.get(web)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'album__main')]")))
        albums = driver.find_elements(By.XPATH, "//a[contains(@class, 'album__main')]")


print(nombres_no_descargados)
# Cerrar el navegador
driver.quit()
