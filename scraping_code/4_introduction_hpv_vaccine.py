import requests

url = "https://ourworldindata.org/grapher/human-papillomavirus-vaccine-immunization-schedule.csv?v=1&csvType=full&useColumnShortNames=true"

response = requests.get(url)
if response.status_code == 200:
    print("Téléchargement réussi.")
    file_name = "introduction_hpv_vaccine.csv"
    with open(file_name, 'wb') as file:
        file.write(response.content)
    print(f"Fichier enregistré sous : {file_name}")
else:
    print(f"Erreur lors du téléchargement : {response.status_code}")

try:
    with open(file_name, 'r', encoding='utf-8') as file:
        contenu = file.read()
        print("Contenu du fichier XSD :\n")
        print(contenu)
except FileNotFoundError:
    print(f"Le fichier {file_name} n'a pas été trouvé. Vérifiez si le téléchargement a réussi.")
