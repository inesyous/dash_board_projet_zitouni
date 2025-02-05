import requests
from bs4 import BeautifulSoup
import os
import pandas as pd

# 📍 Définir le chemin absolu pour stocker les fichiers CSV
save_folder = "/Users/badisbensalem/Desktop/dash_board_projet_zitouni/donnees_vaccination"

# 📂 Créer le dossier s'il n'existe pas
os.makedirs(save_folder, exist_ok=True)

# 🌐 URL de la page contenant les fichiers
url = "https://www.santepubliquefrance.fr/determinants-de-sante/vaccination/articles/donnees-infra-nationales-de-couverture-vaccinale-papillomavirus-humains-hpv"

# 🔽 Télécharger la page
response = requests.get(url)

if response.status_code == 200:
    print("✅ Page téléchargée avec succès.")
    soup = BeautifulSoup(response.content, "html.parser")

    # 🔍 Rechercher les liens contenant "2023" + "jeunes filles" ou "jeunes garçons"
    links = soup.find_all("a", string=lambda text: text and ("2023" in text and ("jeunes filles" in text.lower() or "jeunes garçons" in text.lower())))

    if links:
        print(f"📂 {len(links)} fichiers trouvés.")

        # 📥 Télécharger et convertir chaque fichier XLSX en CSV, puis supprimer le XLSX
        for i, link in enumerate(links):
            file_url = link.get("href")

            # 🛠️ Vérifier si l'URL est relative et la compléter
            if file_url.startswith("/"):
                file_url = "https://www.santepubliquefrance.fr" + file_url  

            # 🏷️ Définir les noms des fichiers avec leur chemin absolu
            if "jeunes filles" in link.text.lower():
                file_xlsx = os.path.join(save_folder, "couverture_vaccinale_2023_filles.xlsx")
                file_csv = os.path.join(save_folder, "couverture_vaccinale_2023_filles.csv")
            elif "jeunes garçons" in link.text.lower():
                file_xlsx = os.path.join(save_folder, "couverture_vaccinale_2023_garcons.xlsx")
                file_csv = os.path.join(save_folder, "couverture_vaccinale_2023_garcons.csv")
            else:
                file_xlsx = os.path.join(save_folder, f"fichier_{i + 1}.xlsx")
                file_csv = os.path.join(save_folder, f"fichier_{i + 1}.csv")

            # 📥 Télécharger le fichier XLSX
            file_response = requests.get(file_url)
            if file_response.status_code == 200:
                with open(file_xlsx, "wb") as file:
                    file.write(file_response.content)
                print(f"✅ Fichier XLSX téléchargé : {file_xlsx}")

                # 🔄 Convertir en CSV
                try:
                    df = pd.read_excel(file_xlsx, engine="openpyxl")  # Lire le fichier XLSX
                    df.to_csv(file_csv, index=False, sep=";")  # Sauvegarder en CSV
                    print(f"✅ Fichier converti en CSV : {file_csv}")

                    # 🗑️ Supprimer le fichier XLSX après conversion
                    os.remove(file_xlsx)
                    print(f"🗑️ Fichier XLSX supprimé : {file_xlsx}")

                except Exception as e:
                    print(f"❌ Erreur de conversion {file_xlsx} -> CSV : {e}")

            else:
                print(f"❌ Erreur lors du téléchargement du fichier {i + 1} : {file_response.status_code}")

    else:
        print("⚠️ Aucun fichier correspondant trouvé.")
else:
    print(f"❌ Erreur lors du téléchargement de la page : {response.status_code}")
