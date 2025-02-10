import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import requests
import numpy as np

# --- Chargement et préparation des données ---

# Chemin mis à jour pour le CSV
file_path_depistage = "/Users/badisbensalem/Desktop/depistage2023.csv"
df_depistage = pd.read_csv(file_path_depistage, sep=",")

# Renommage des colonnes pour correspondre aux noms utilisés dans le GeoJSON
df_depistage.columns = ['code_region', 'libelle_region', 'population', 'incidence', 'depistage_global',
                         'depistage_vingtaine', 'trentaine_trancheA', 'trentaine_trancheB',
                         'quarantaine_trancheA', 'quarantaine_trancheB', 'cinquantaine_trancheA',
                         'cinquantaine_trancheB', 'soixantaine']

# Correction des noms pour qu'ils correspondent aux propriétés du GeoJSON
corrections_regions = {
    "Paca": "Provence-Alpes-Côte d'Azur",
    "Ile de France": "Île-de-France",
    "Grand-Est": "Grand Est",
    "Bourgogne - Franche - Comté": "Bourgogne-Franche-Comté",
    "Centre": "Centre-Val de Loire",
    "Nouvelle Aquitaine": "Nouvelle-Aquitaine",
    "Auvergne - Rhône-Alpes": "Auvergne-Rhône-Alpes"
}
df_depistage['libelle_region'] = df_depistage['libelle_region'].replace(corrections_regions)

# --- Chargement du GeoJSON des régions françaises ---
geojson_url = "https://france-geojson.gregoiredavid.fr/repo/regions.geojson"
geojson_data = requests.get(geojson_url).json()

# --- Fonctions de transformation géométrique ---

def translate_geometry(geometry, delta_lon, delta_lat):
    """Décale la géométrie de delta_lon et delta_lat."""
    if geometry["type"] == "Polygon":
        new_coords = []
        for ring in geometry["coordinates"]:
            new_coords.append([[lon + delta_lon, lat + delta_lat] for lon, lat in ring])
        geometry["coordinates"] = new_coords
    elif geometry["type"] == "MultiPolygon":
        new_coords = []
        for polygon in geometry["coordinates"]:
            new_polygon = []
            for ring in polygon:
                new_polygon.append([[lon + delta_lon, lat + delta_lat] for lon, lat in ring])
            new_coords.append(new_polygon)
        geometry["coordinates"] = new_coords
    return geometry

def scale_geometry(geometry, scale_factor, center_lon, center_lat):
    """Redimensionne la géométrie autour de son centroïde."""
    if geometry["type"] == "Polygon":
        new_coords = []
        for ring in geometry["coordinates"]:
            new_coords.append([[(lon - center_lon) * scale_factor + center_lon,
                                (lat - center_lat) * scale_factor + center_lat]
                               for lon, lat in ring])
        geometry["coordinates"] = new_coords
    elif geometry["type"] == "MultiPolygon":
        new_coords = []
        for polygon in geometry["coordinates"]:
            new_polygon = []
            for ring in polygon:
                new_polygon.append([[(lon - center_lon) * scale_factor + center_lon,
                                     (lat - center_lat) * scale_factor + center_lat]
                                    for lon, lat in ring])
            new_coords.append(new_polygon)
        geometry["coordinates"] = new_coords
    return geometry

def compute_bounding_box(geometry):
    """Calcule la boîte englobante (min/max longitude et latitude) de la géométrie."""
    lons, lats = [], []
    if geometry["type"] == "Polygon":
        for ring in geometry["coordinates"]:
            for lon, lat in ring:
                lons.append(lon)
                lats.append(lat)
    elif geometry["type"] == "MultiPolygon":
        for polygon in geometry["coordinates"]:
            for ring in polygon:
                for lon, lat in ring:
                    lons.append(lon)
                    lats.append(lat)
    return min(lons), max(lons), min(lats), max(lats)

def scale_and_translate_geometry(geometry, target_dim, target_position):
    """
    Redimensionne la géométrie pour que sa dimension maximale soit target_dim,
    puis la translate pour que son centroïde corresponde à target_position.
    """
    min_lon, max_lon, min_lat, max_lat = compute_bounding_box(geometry)
    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2

    current_dim = max(max_lon - min_lon, max_lat - min_lat)
    scale_factor = target_dim / current_dim if current_dim else 1

    scaled_geo = scale_geometry(geometry, scale_factor, center_lon, center_lat)
    min_lon2, max_lon2, min_lat2, max_lat2 = compute_bounding_box(scaled_geo)
    new_center_lon = (min_lon2 + max_lon2) / 2
    new_center_lat = (min_lat2 + max_lat2) / 2

    delta_lon = target_position[0] - new_center_lon
    delta_lat = target_position[1] - new_center_lat
    return translate_geometry(scaled_geo, delta_lon, delta_lat)

# --- Repositionnement des DOM-TOM ---
# La France métropolitaine reste à son emplacement d'origine.
# Les DOM-TOM (Guadeloupe, Martinique, Guyane, La Réunion, Mayotte) seront repositionnées à droite.
target_positions = {
    "Guadeloupe": (-8, 49),
    "Martinique": (-8, 47),
    "Guyane": (-8, 45),
    "La Réunion": (-8, 43),
    "Mayotte": (-8, 41)
}
target_dim = 2.0  # Dimension fixe pour les DOM-TOM

for feature in geojson_data["features"]:
    name = feature["properties"]["nom"]
    if name in target_positions:
        feature["geometry"] = scale_and_translate_geometry(feature["geometry"],
                                                            target_dim,
                                                            target_positions[name])

# --- Création de l'application Dash ---

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Taux de Dépistage par Région en France",
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '20px'}),
    html.Div([
        dcc.Dropdown(
            id='age-group-dropdown',
            options=[
                {'label': 'Dépistage Global', 'value': 'depistage_global'},
                {'label': 'Vingtaine', 'value': 'depistage_vingtaine'},
                {'label': 'Trentaine Tranche A', 'value': 'trentaine_trancheA'},
                {'label': 'Trentaine Tranche B', 'value': 'trentaine_trancheB'},
                {'label': 'Quarantaine Tranche A', 'value': 'quarantaine_trancheA'},
                {'label': 'Quarantaine Tranche B', 'value': 'quarantaine_trancheB'},
                {'label': 'Cinquantaine Tranche A', 'value': 'cinquantaine_trancheA'},
                {'label': 'Cinquantaine Tranche B', 'value': 'cinquantaine_trancheB'},
                {'label': 'Soixantaine', 'value': 'soixantaine'}
            ],
            value='depistage_global',
            clearable=False,
            style={'width': '50%', 'margin': '20px auto'}
        )
    ], style={'textAlign': 'center'}),
    dcc.Graph(
        id="taux-depistage",
        style={'height': '800px'},
        config={
            "scrollZoom": False,    # Désactive le zoom à la molette
            "doubleClick": False,   # Désactive le double-clic
            "displayModeBar": False # Masque la barre d'outils
        }
    )
], style={'fontFamily': 'Arial, sans-serif'})

@app.callback(
    Output('taux-depistage', 'figure'),
    Input('age-group-dropdown', 'value')
)
def update_map(selected_age_group):
    fig = px.choropleth(
        df_depistage,
        geojson=geojson_data,
        locations="libelle_region",
        featureidkey="properties.nom",
        color=selected_age_group,
        hover_name="libelle_region",
        hover_data={
            "population": True,
            "incidence": True,
            selected_age_group: ':.2f'
        },
        color_continuous_scale=[
            [0, 'rgb(70, 0, 90)'],
            [0.25, 'rgb(100, 0, 120)'],
            [0.5, 'rgb(0, 100, 80)'],
            [0.75, 'rgb(0, 150, 80)'],
            [1, 'rgb(150, 255, 0)']
        ],
        labels={
            selected_age_group: "Taux de dépistage",
            "population": "Population",
            "incidence": "Incidence"
        }
    )

    # On centre la vue sur la zone couverte par les features (France métropolitaine et DOM-TOM repositionnées)
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        resolution=50,
        showcountries=False,
        showcoastlines=False,
        showocean=False,
        projection_type="mercator"
    )

    # Pour "figurer" une carte fixe, on définit le dragmode sur "zoom" (donc aucun déplacement par glisser)
    # et on fixe la vue avec uirevision afin que toute modification utilisateur soit réinitialisée.
    fig.update_layout(
        dragmode="zoom",
        uirevision="fixed",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    return fig

if __name__ == "__main__":
    app.run_server(debug=True)