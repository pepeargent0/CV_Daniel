import os
import zipfile
import shutil
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unicodedata

# URL del CSV con los enlaces de descarga
csv_url = 'https://docs.google.com/spreadsheets/d/1azJrrovCMYBeRasAOwh-87nVSxQPdjRs2AfBoKy97-0/export?format=csv'
output_directory = 'drive'
temp_directory = 'temp_dataset'

# Crear los directorios necesarios
os.makedirs(output_directory, exist_ok=True)
os.makedirs(temp_directory, exist_ok=True)

# Configuración del navegador para la descarga automática
firefox_options = webdriver.FirefoxOptions()
firefox_options.set_preference('browser.download.folderList', 2)  # Use custom download path
firefox_options.set_preference('browser.download.manager.showWhenStarting', False)
firefox_options.set_preference('browser.download.dir', os.path.abspath(output_directory))
firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip,application/octet-stream')

driver = webdriver.Firefox(options=firefox_options)
wait = WebDriverWait(driver, 60)

# Descargar el archivo CSV con los enlaces de descarga
response = requests.get(csv_url)
url_drives = []
if response.status_code == 200:
    drives = response.content.decode('utf-8').split('\n')
    for i in range(1, len(drives)):
        drives[i] = drives[i].replace('no con jpeg y txt', '')
        drives[i] = drives[i].replace('"', '')
        columns = drives[i].split(',')
        link = columns[-1].strip()
        url_drives.append(link)
else:
    print(f"Error al acceder a la hoja de cálculo: {response.status_code}")

# Descargar los archivos desde Google Drive
for folder_url in range(1, len(url_drives)):
    driver.get(url_drives[folder_url])
    time.sleep(5)
    try:
        download_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, '//*[contains(text(), "Descargar") or contains(text(), "Descargar")]')))
        download_button.click()
        time.sleep(20)  # Esperar a que la descarga comience
    except Exception as e:
        print(f"Error al intentar descargar archivos de la carpeta {url_drives[folder_url]}: {e}")
    print(f"Descarga iniciada desde la carpeta: {url_drives[folder_url]}")

driver.quit()
print("Descarga completada.")

# Directorios finales para las imágenes y las etiquetas
images_directory = 'dataset_tmp/images'
labels_directory = 'dataset_tmp/labels'
extensiones_imagenes = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

# Crear directorios de imágenes y etiquetas si no existen
os.makedirs(images_directory, exist_ok=True)
os.makedirs(labels_directory, exist_ok=True)


# Función para normalizar nombres de archivo
def normalize_filename(filename):
    filename = filename.lower()
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    filename = filename.replace(' ', '-').replace('_', '')
    return filename


# Función para copiar pares de archivos a los directorios correspondientes
def copiar_pares(pares, img_dest, lbl_dest):
    for imagen_path, txt_path in pares:
        imagen_name = normalize_filename(os.path.basename(imagen_path))
        txt_name = normalize_filename(os.path.basename(txt_path))

        shutil.copy(imagen_path, os.path.join(img_dest, imagen_name))
        shutil.copy(txt_path, os.path.join(lbl_dest, txt_name))

        os.remove(imagen_path)
        os.remove(txt_path)


# Procesar los archivos descargados
if os.path.exists(output_directory):
    for file in os.listdir(output_directory):
        if file.endswith('.zip'):
            file_path = os.path.join(output_directory, file)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_directory)
                print(f"Unzipped '{file}' in '{temp_directory}'")

    for item in os.listdir(temp_directory):
        item_path = os.path.join(temp_directory, item)
        if os.path.isdir(item_path):
            pares_imagen_txt = []

            for archivo in os.listdir(item_path):
                if os.path.splitext(archivo)[1].lower() in extensiones_imagenes:
                    archivo_txt = os.path.splitext(archivo)[0] + '.txt'
                    if archivo_txt in os.listdir(item_path):
                        pares_imagen_txt.append(
                            (os.path.join(item_path, archivo), os.path.join(item_path, archivo_txt)))
                    else:
                        os.remove(os.path.join(item_path, archivo))
                        print(f"Imagen '{archivo}' eliminada porque no tiene un archivo .txt correspondiente.")

            copiar_pares(pares_imagen_txt, images_directory, labels_directory)
            print(f"Imágenes y etiquetas movidas desde '{item}'")

    # Limpiar la carpeta de descarga
    shutil.rmtree(output_directory)
    print(f"Carpeta '{output_directory}' eliminada.")
else:
    print(f"El directorio '{output_directory}' no existe.")
