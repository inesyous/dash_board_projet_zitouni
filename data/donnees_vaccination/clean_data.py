import pandas as pd
import os
import requests
import re

# 📥 Charger les données CSV avec le bon séparateur
file_path = "/Users/badisbensalem/Desktop/dash_board_projet_zitouni/data/donnees_vaccination/couverture_vaccinale_2023_garcons.csv"
df = pd.read_csv(file_path, sep=';', dtype=str)

# 🛠️ Nettoyage des données

# Supprimer la première colonne
df = df.iloc[:, 1:]

# Supprimer les lignes avec une seule valeur renseignée
df = df.dropna(thresh=2)

# Supprimer les lignes complètement vides
df = df.dropna(how='all')

# Renommer les colonnes avec la première ligne des données
df.columns = df.iloc[0]  # Utiliser la première ligne comme en-têtes
df = df[1:].reset_index(drop=True)  # Supprimer cette ligne et réinitialiser l'index

# 🛠️ Nettoyage des noms des régions
df.rename(columns={"Année de\nnaissance": "Région"}, inplace=True)  # Renommer correctement la colonne des régions

# Supprimer les espaces en début/fin et remplacer les retours à la ligne par un espace
df["Région"] = df["Région"].str.strip().str.replace("\n", " ")

# Correction spécifique pour "Hauts-de-France" : suppression de l'espace après le tiret
df["Région"] = df["Région"].str.replace(r'Hauts-de-\s+', 'Hauts-de-', regex=True)

# Corriger certains accents ou caractères spéciaux
df["Région"] = df["Région"].str.replace("Î", "I").str.replace("’", "'")

# 🛠️ Correction des noms de régions pour correspondre au GeoJSON
corrections_regions = {
    "Paca": "Provence-Alpes-Côte d'Azur",
    "Ile de France": "Île-de-France",
    "Grand-Est": "Grand Est",
    "Bourgogne - Franche - Comté": "Bourgogne-Franche-Comté",
    "Centre": "Centre-Val de Loire",
    "Nouvelle Aquitaine": "Nouvelle-Aquitaine",
    "Auvergne - Rhône-Alpes": "Auvergne-Rhône-Alpes"
}
df["Région"] = df["Région"].replace(corrections_regions)

# ★ Nouvelle étape : Standardiser les noms de colonnes pour les années
def clean_year_name(col):
    if col == "Région":
        return col
    return re.sub(r'\.0$', '', col)

df.columns = [clean_year_name(col) for col in df.columns]

# 🛠️ Conversion des valeurs en numériques pour toutes les colonnes d'années
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 🛠️ Remplacer les valeurs manquantes par 0
df.fillna(0, inplace=True)

# 📥 Charger les données GeoJSON des régions françaises
geojson_url = "https://france-geojson.gregoiredavid.fr/repo/regions.geojson"
geojson_data = requests.get(geojson_url).json()

# 📌 Vérifier si toutes les régions sont reconnues
geo_regions = [feature["properties"]["nom"] for feature in geojson_data["features"]]
regions_non_trouvees = set(df["Région"]) - set(geo_regions)

if regions_non_trouvees:
    print("❌ Régions non reconnues :", regions_non_trouvees)
else:
    print("✅ Toutes les régions sont reconnues !")

# 📁 Sauvegarder le fichier nettoyé
file_path_cleaned = "/Users/badisbensalem/Desktop/dash_board_projet_zitouni/data/donnees_vaccination/couverture_vaccinale_2023_garcons_nettoye.csv"
df.to_csv(file_path_cleaned, index=False, sep=';')

# ✅ Vérification de l'enregistrement
if os.path.exists(file_path_cleaned):
    print(f"✅ Fichier nettoyé enregistré avec succès : {file_path_cleaned}")
else:
    print(f"❌ ERREUR : Le fichier nettoyé n'a pas été enregistré correctement.")