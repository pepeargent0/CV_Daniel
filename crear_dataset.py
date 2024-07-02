import requests
csv_url = 'https://docs.google.com/spreadsheets/d/1azJrrovCMYBeRasAOwh-87nVSxQPdjRs2AfBoKy97-0/export?format=csv'
response = requests.get(csv_url)
url_drives = []
if response.status_code == 200:
    drives = response.content.decode('utf-8').split('\n')
    for i in range(1,len(drives)):
        drives[i] = drives[i].replace('no con jpeg y txt','')
        drives[i] = drives[i].replace('"', '')
        columnas = drives[i].split(',')
        pos = len(columnas) - 1
        url_drives.append(columnas[pos].split('\r')[0])
else:
    print(f"Error al acceder a la hoja de cálculo: {response.status_code}")
print(url_drives)