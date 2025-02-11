import requests


url = "https://www.data.gouv.fr/fr/datasets/r/66ca937f-cd53-4612-a4f2-e130f52e3493"


response = requests.get(url)


file_name = "depistage2023.csv"

try:
    with open(file_name, 'r', encoding='utf-8') as file:
        contenu = file.read()
        print("Contenu du fichier XSD :\n")
except FileNotFoundError:
    print(f"Le fichier {file_name} pas été trouvé. ")