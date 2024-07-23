import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
                By.XPATH, '//*[contains(text(), "Descargar") or contains(text(), "Download")]')))
        download_button.click()
        time.sleep(20)  # Esperar a que la descarga comience
    except Exception as e:
        print(f"Error al intentar descargar archivos de la carpeta {url_drives[folder_url]}: {e}")
    print(f"Descarga iniciada desde la carpeta: {url_drives[folder_url]}")

driver.quit()
print("Descarga completada.")
