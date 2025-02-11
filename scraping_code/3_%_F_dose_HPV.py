import pandas as pd
import requests

df = pd.read_csv("https://ourworldindata.org/grapher/coverage-of-the-human-papillomavirus-vaccine.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

metadata = requests.get("https://ourworldindata.org/grapher/coverage-of-the-human-papillomavirus-vaccine.metadata.json?v=1&csvType=full&useColumnShortNames=true").json()
# Faire la requête HTTP pour obtenir la page

df.to_csv("HPV_vaccine_data.csv", index=False)
print("Fichier enregistré : HPV_vaccine_data.csv")
print(df.columns)