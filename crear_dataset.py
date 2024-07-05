import os
import zipfile
import shutil
import random
"""
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
csv_url = 'https://docs.google.com/spreadsheets/d/1azJrrovCMYBeRasAOwh-87nVSxQPdjRs2AfBoKy97-0/export?format=csv'
output_directory = 'downloaded_files'
os.makedirs(output_directory, exist_ok=True)

firefox_options = webdriver.FirefoxOptions()
firefox_options.set_preference('browser.download.folderList', 2)  # Use custom download path
firefox_options.set_preference('browser.download.manager.showWhenStarting', False)
firefox_options.set_preference('browser.download.dir', os.path.abspath(output_directory))
firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip,application/octet-stream')

driver = webdriver.Firefox(options=firefox_options)
wait = WebDriverWait(driver, 60)
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
for folder_url in url_drives:
    driver.get(folder_url)
    time.sleep(5)
    try:
        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Descargar") or contains(text(), "Descargar")]')))
        download_button.click()
        time.sleep(20)  # Esperar a que la descarga comience
    except Exception as e:
        print(f"Error al intentar descargar archivos de la carpeta {folder_url}: {e}")
    print(f"Descarga iniciada desde la carpeta: {folder_url}")
driver.quit()
print("Descarga completada.")
"""
output_directory = 'downloaded_files'
train_images_directory = 'dataset/train/images'
train_labels_directory = 'dataset/train/labels'
valid_images_directory = 'dataset/valid/images'
valid_labels_directory = 'dataset/valid/labels'
extensiones_imagenes = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

# Crear directorios de entrenamiento y validación si no existen
os.makedirs(train_images_directory, exist_ok=True)
os.makedirs(train_labels_directory, exist_ok=True)
os.makedirs(valid_images_directory, exist_ok=True)
os.makedirs(valid_labels_directory, exist_ok=True)


# Función para copiar pares de archivos a los directorios correspondientes
def copiar_pares(pares, img_dest, lbl_dest):
    for imagen_path, txt_path in pares:
        shutil.copy(imagen_path, img_dest)
        shutil.copy(txt_path, lbl_dest)

if os.path.exists(output_directory):
    for file in os.listdir(output_directory):
        if file.endswith('.zip'):
            file_path = os.path.join(output_directory, file)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(output_directory)
                print(f"Unzipped '{file}' in '{output_directory}'")
            os.remove(file_path)

    total_imagenes = 0
    imagenes_con_txt = 0
    imagenes_sin_txt = 0

    for item in os.listdir(output_directory):
        item_path = os.path.join(output_directory, item)
        if os.path.isdir(item_path):
            num_files = len([name for name in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, name))])
            print(f"El directorio '{item}' contiene {num_files} archivos")

            total_imagenes_directorio = 0
            imagenes_con_txt_directorio = 0
            imagenes_sin_txt_directorio = 0
            pares_imagen_txt = []

            for archivo in os.listdir(item_path):
                if os.path.splitext(archivo)[1].lower() in extensiones_imagenes:
                    total_imagenes_directorio += 1
                    archivo_txt = os.path.splitext(archivo)[0] + '.txt'
                    if archivo_txt in os.listdir(item_path):
                        imagenes_con_txt_directorio += 1
                        pares_imagen_txt.append(
                            (os.path.join(item_path, archivo), os.path.join(item_path, archivo_txt)))
                    else:
                        imagenes_sin_txt_directorio += 1
                        os.remove(os.path.join(item_path, archivo))
                        print(f"Imagen '{archivo}' eliminada porque no tiene un archivo .txt correspondiente.")

            print(f"Total de imágenes en '{item}': {total_imagenes_directorio}")
            print(f"Imágenes con archivo .txt correspondiente en '{item}': {imagenes_con_txt_directorio}")
            print(f"Imágenes sin archivo .txt correspondiente en '{item}': {imagenes_sin_txt_directorio}")

            num_train = int(0.8 * len(pares_imagen_txt))
            num_valid = len(pares_imagen_txt) - num_train

            random.shuffle(pares_imagen_txt)

            pares_train = pares_imagen_txt[:num_train]
            pares_valid = pares_imagen_txt[num_train:]

            copiar_pares(pares_train, train_images_directory, train_labels_directory)
            copiar_pares(pares_valid, valid_images_directory, valid_labels_directory)

            print(f"Imágenes movidas al conjunto de entrenamiento desde '{item}': {num_train}")
            print(f"Imágenes movidas al conjunto de validación desde '{item}': {num_valid}")

    print(f"\nTotal de imágenes procesadas: {total_imagenes}")
    print(f"Imágenes con archivo .txt correspondiente: {imagenes_con_txt}")
    print(f"Imágenes sin archivo .txt correspondiente: {imagenes_sin_txt}")

else:
    print(f"El directorio '{output_directory}' no existe.")
