import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, requests
import dash
from dash import dcc, html, Input, Output, State

# =============================================================================
# 1. Chargement des données
# =============================================================================

# Chemins vers vos fichiers CSV (à adapter)
file_path_filles = "/Users/badisbensalem/Desktop/dash_board_projet_zitouni/data/donnees_vaccination/couverture_vaccinale_2023_filles_nettoye.csv"
file_path_garcons = "/Users/badisbensalem/Desktop/dash_board_projet_zitouni/data/donnees_vaccination/couverture_vaccinale_2023_garcons_nettoye.csv"

# Chargement des données pour filles et garçons
df_filles = pd.read_csv(file_path_filles, sep=";")
df_garcons = pd.read_csv(file_path_garcons, sep=";")

# =============================================================================
# 2. Préparation des données et harmonisation des noms de régions
# =============================================================================

for df in [df_filles, df_garcons]:
    if "Année de\nnaissance" in df.columns:
        df.rename(columns={"Année de\nnaissance": "Région"}, inplace=True)

corrections_regions = {
    "Paca": "Provence-Alpes-Côte d'Azur",
    "Ile de France": "Île-de-France",
    "Grand-Est": "Grand Est",
    "Bourgogne - Franche - Comté": "Bourgogne-Franche-Comté",
    "Centre": "Centre-Val de Loire",
    "Nouvelle Aquitaine": "Nouvelle-Aquitaine",
    "Auvergne - Rhône-Alpes": "Auvergne-Rhône-Alpes"
}
for df in [df_filles, df_garcons]:
    df["Région"] = df["Région"].replace(corrections_regions)

# =============================================================================
# 3. Chargement et ajustement du GeoJSON pour les régions françaises
# =============================================================================

geojson_url = "https://france-geojson.gregoiredavid.fr/repo/regions.geojson"
geojson_data = requests.get(geojson_url).json()

def translate_geometry(geometry, delta_lon, delta_lat):
    if geometry["type"] == "Polygon":
        new_coords = []
        for ring in geometry["coordinates"]:
            new_ring = [[lon + delta_lon, lat + delta_lat] for lon, lat in ring]
            new_coords.append(new_ring)
        geometry["coordinates"] = new_coords
    elif geometry["type"] == "MultiPolygon":
        new_coords = []
        for polygon in geometry["coordinates"]:
            new_polygon = []
            for ring in polygon:
                new_ring = [[lon + delta_lon, lat + delta_lat] for lon, lat in ring]
                new_polygon.append(new_ring)
            new_coords.append(new_polygon)
        geometry["coordinates"] = new_coords
    return geometry

def scale_geometry(geometry, scale_factor, center_lon, center_lat):
    if geometry["type"] == "Polygon":
        new_coords = []
        for ring in geometry["coordinates"]:
            new_ring = []
            for lon, lat in ring:
                scaled_lon = (lon - center_lon) * scale_factor + center_lon
                scaled_lat = (lat - center_lat) * scale_factor + center_lat
                new_ring.append([scaled_lon, scaled_lat])
            new_coords.append(new_ring)
        geometry["coordinates"] = new_coords
    elif geometry["type"] == "MultiPolygon":
        new_coords = []
        for polygon in geometry["coordinates"]:
            new_polygon = []
            for ring in polygon:
                new_ring = []
                for lon, lat in ring:
                    scaled_lon = (lon - center_lon) * scale_factor + center_lon
                    scaled_lat = (lat - center_lat) * scale_factor + center_lat
                    new_ring.append([scaled_lon, scaled_lat])
                new_polygon.append(new_ring)
            new_coords.append(new_polygon)
        geometry["coordinates"] = new_coords
    return geometry

def compute_bounding_box(geometry):
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
    min_lon, max_lon, min_lat, max_lat = compute_bounding_box(geometry)
    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2

    current_max_dim = max(max_lon - min_lon, max_lat - min_lat)
    scale_factor = target_dim / current_max_dim if current_max_dim else 1

    scaled_geometry = scale_geometry(geometry, scale_factor, center_lon, center_lat)
    min_lon2, max_lon2, min_lat2, max_lat2 = compute_bounding_box(scaled_geometry)
    new_center_lon = (min_lon2 + max_lon2) / 2
    new_center_lat = (min_lat2 + max_lat2) / 2

    delta_lon = target_position[0] - new_center_lon
    delta_lat = target_position[1] - new_center_lat
    final_geometry = translate_geometry(scaled_geometry, delta_lon, delta_lat)
    return final_geometry

target_positions = {
    "Guadeloupe": (-8, 49),
    "Martinique": (-8, 47),
    "Guyane": (-8, 45),
    "La Réunion": (-8, 43),
    "Mayotte": (-8, 41)
}
target_dim = 2.0

for feature in geojson_data["features"]:
    name = feature["properties"]["nom"]
    if name in target_positions:
        feature["geometry"] = scale_and_translate_geometry(
            feature["geometry"],
            target_dim=target_dim,
            target_position=target_positions[name]
        )

# =============================================================================
# 4. Préparation des données pour le graphique d'évolution (format long)
# =============================================================================

df_filles_melted = df_filles.melt(id_vars=["Région"], var_name="Année", value_name="Couverture Vaccinale")
df_garcons_melted = df_garcons.melt(id_vars=["Région"], var_name="Année", value_name="Couverture Vaccinale")

for df_melt in [df_filles_melted, df_garcons_melted]:
    # On convertit l'année en entier et on ajoute 16
    df_melt["Année"] = df_melt["Année"].astype(int) + 16

# =============================================================================
# 5. Création de l'application Dash et de la mise en page
# =============================================================================

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Couverture Vaccinale à 16 ans en France", style={'textAlign': 'center'}),
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='sex-dropdown',
                options=[
                    {'label': 'Filles', 'value': 'fille'},
                    {'label': 'Garçons', 'value': 'garcon'}
                ],
                value='fille',
                clearable=False,
                style={'width': '150px'}
            )
        ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '20px'}),
        
        html.Div([
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(int(col) + 16), 'value': str(col)}
                         for col in df_filles.columns if col != "Région"],
                value=df_filles.columns[1],
                clearable=False,
                style={'width': '150px'}
            )
        ], style={'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    html.Div(
        dcc.Graph(
            id='map',
            config={'displayModeBar': False, 'scrollZoom': False}
        ),
        id="map-container"
    ),
    
    # Popup pour le mini-graphique avec configuration du mode bar
    html.Div(
        dcc.Graph(
            id='popup-graph',
            config={
                'displayModeBar': True,
                'modeBarButtonsToRemove': [
                    "zoom2d", "pan2d", "select2d", "lasso2d",
                    "zoomIn2d", "zoomOut2d", "autoScale2d",
                    "hoverClosestCartesian", "hoverCompareCartesian",
                    "toggleSpikelines", "toImage"
                ],
                'displaylogo': False,
                'scrollZoom': False
            },
            style={'height': '100%', 'width': '100%'}
        ),
        id='popup',
        style={
            'position': 'absolute',
            'display': 'none',  # Masqué par défaut
            'width': '300px',
            'height': '200px',
            'border': '1px solid #ccc',
            'background-color': 'white',
            'zIndex': '1000',
            'box-shadow': '2px 2px 10px rgba(0,0,0,0.2)',
            'padding': '5px'
        }
    ),
    
    # Script pour positionner le popup à l'endroit du clic sur la carte
    html.Script("""
    document.addEventListener('DOMContentLoaded', function() {
        var mapContainer = document.getElementById('map-container');
        if(mapContainer){
            mapContainer.addEventListener('click', function(e) {
                var popup = document.getElementById('popup');
                popup.style.left = (e.clientX + 10) + 'px';
                popup.style.top = (e.clientY + 10) + 'px';
            });
        }
    });
    """)
])

# =============================================================================
# 6. Callbacks
# =============================================================================

@app.callback(
    [Output('year-dropdown', 'options'),
     Output('year-dropdown', 'value')],
    [Input('sex-dropdown', 'value')]
)
def update_year_dropdown(selected_sex):
    if selected_sex == 'garcon':
        desired_years = ['2006', '2007']
        available_years = [year for year in desired_years if year in df_garcons.columns]
        if not available_years:
            available_years = [str(col) for col in df_garcons.columns if col != "Région"]
        options = [{'label': str(int(year) + 16), 'value': year} for year in available_years]
        default_value = available_years[0]
    else:
        available_years = [str(col) for col in df_filles.columns if col != "Région"]
        options = [{'label': str(int(year) + 16), 'value': year} for year in available_years]
        default_value = available_years[0]
    return options, default_value

@app.callback(
    Output('map', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('sex-dropdown', 'value')]
)
def update_map(selected_year, selected_sex):
    if selected_sex == 'garcon':
        available_years = [str(col) for col in df_garcons.columns if col != "Région"]
        if selected_year not in available_years:
            selected_year = available_years[0] if available_years else None
        df_selected = df_garcons[['Région', selected_year]].copy()
    else:
        available_years = [str(col) for col in df_filles.columns if col != "Région"]
        if selected_year not in available_years:
            selected_year = available_years[0] if available_years else None
        df_selected = df_filles[['Région', selected_year]].copy()

    df_selected[selected_year] = pd.to_numeric(df_selected[selected_year], errors='coerce').fillna(0)
    
    fig = px.choropleth_mapbox(
        df_selected,
        geojson=geojson_data,
        locations="Région",
        featureidkey="properties.nom",
        color=selected_year,
        color_continuous_scale="Viridis",
        range_color=[0, 50],
        mapbox_style="white-bg",
        zoom=4.0,
        center={"lat": 45.5, "lon": 4.5},
        opacity=0.85,
        hover_data=["Région", selected_year],
        labels={selected_year: "Couverture vaccinale (%)"}
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        dragmode=False
    )
    return fig

@app.callback(
    [Output('popup-graph', 'figure'),
     Output('popup', 'style')],
    [Input('map', 'clickData'),
     Input('sex-dropdown', 'value')],
    [State('popup', 'style')]
)
def update_popup_graph(clickData, selected_sex, current_style):
    if clickData is None:
        if current_style is None:
            current_style = {}
        current_style['display'] = 'none'
        return go.Figure(), current_style

    region = clickData['points'][0].get('location')
    if region is None:
        if current_style is None:
            current_style = {}
        current_style['display'] = 'none'
        return go.Figure(), current_style

    if selected_sex == 'garcon':
        df_filtered = df_garcons_melted[df_garcons_melted['Région'] == region]
    else:
        df_filtered = df_filles_melted[df_filles_melted['Région'] == region]
    df_filtered = df_filtered.sort_values('Année')
    
    fig = px.line(
        df_filtered, 
        x='Année', 
        y='Couverture Vaccinale',
        title=f"Évolution en {region}",
        labels={'Année': 'Année', 'Couverture Vaccinale': 'Pourcentage'}
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        title_font=dict(size=12),
        font=dict(size=10)
    )
    # Fixer l'axe des ordonnées entre 0 et 100
    fig.update_yaxes(range=[0, 100])
    
    if current_style is None:
        current_style = {}
    current_style['display'] = 'block'
    return fig, current_style

if __name__ == '__main__':
    app.run_server(debug=True)