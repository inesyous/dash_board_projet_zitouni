import requests

# URL de la base de données
url = "https://ourworldindata.org/grapher/human-papillomavirus-vaccine-immunization-schedule.csv?v=1&csvType=full&useColumnShortNames=true"

# Télécharger le fichier
response = requests.get(url)
if response.status_code == 200:
    print("Téléchargement réussi.")
    # Enregistrer le fichier localement (par exemple, sous le nom 'base_donnees.csv')
    file_name = "introduction_hpv_vaccine.csv"
    with open(file_name, 'wb') as file:
        file.write(response.content)
    print(f"Fichier enregistré sous : {file_name}")
else:
    print(f"Erreur lors du téléchargement : {response.status_code}")

# Lire le fichier téléchargé
file_name = "repartition_cancers.csv"

try:
    with open(file_name, 'r', encoding='utf-8') as file:
        contenu = file.read()
        print("Contenu du fichier XSD :\n")
        print(contenu)
except FileNotFoundError:
    print(f"Le fichier {file_name} n'a pas été trouvé. Vérifiez si le téléchargement a réussi.")
