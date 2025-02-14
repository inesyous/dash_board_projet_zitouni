import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import dash
import dash_bootstrap_components as dbc

# Styles figure1
virus_animation_style = {
    'main-container': {
        'color': '#fff',
        'fontFamily': 'Arial, sans-serif',
        'margin': 0,
        'padding': '2vh',
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'justifyContent': 'center',
        'height': 'calc(25vw)',
        'max-width': '30vw',
        'position': 'relative'
    },

    'container-base': {
        'position': 'absolute',
        'cursor': 'pointer',
        'padding': '1vh',
        'transition': 'transform 0.2s ease',
        'width': '30%',
        'height': '30%',
        'transform': 'translate(-50%, -50%)'
    },
    'virus': {
        'position': 'absolute',
        'top': '50%',
        'left': '50%',
        'width': '50%',
        'height': '50%',
        'transform': 'translate(-50%, -50%)',
        'animation': 'float 3s ease-in-out infinite'
    },
    'disease-img': {
        'width': '90%',
        'height': '90%',
        'objectFit': 'cover',
        'border': '0.3vh solid black',
        'borderRadius': '15%'
    }
}


disease_positions = {
    'anus': {'top': '20%', 'left': '50%'},
    'oropharynx': {'top': '50%', 'left': '80%'},
    'penis': {'top': '80%', 'left': '50%'},
    'vagin': {'top': '50%', 'left': '20%'}
}


info_mapping = {
    "Anus": ["95.7% of anal cancer cases are caused by a human papillomavirus (HPV) infection."],
    "Voies Aérodigestives Supérieures": [
        "Oropharynx : 95.1% of oropharyngeal cancer cases are caused by an HPV infection.",
        "Oral Cavity : 92.7% of oral cavity cancer cases are caused by an HPV infection.",
        "Larynx : 77.8% of laryngeal cancer cases are caused by an HPV infection."
    ],
    "Pénis": ["88.1% of penile cancer cases are caused by a human papillomavirus (HPV) infection."],
    "Vagin": [
        "Vulva : 92.8% of vulvar cancer cases are caused by a human papillomavirus (HPV) infection.",
        "Cervix (Uterine Cervix) : 89.3% of cervical cancer cases are caused by an HPV infection.",
        "Vagina : 85.6% of vaginal cancer cases are caused by an HPV infection."
        ]
}


def create_virus_animation():
    disease_info = [
        ("anus", "1_cancer_anal(6).png"),
        ("oropharynx", "1_cancer_Oropharynx(3).png"),
        ("penis", "1_cancer_penis(4).png"),
        ("vagin", "1_cancer_vagin(5).png")
    ]

    disease_divs = [
        html.Div([
            html.Img(
                src=f"https://raw.githubusercontent.com/badis2203/dash_board_projet_zitouni/main/src/image_dash/{img}",
                style=virus_animation_style['disease-img']
            )
        ], id=f'{disease}-container', style={**virus_animation_style['container-base'], **disease_positions[disease]})
        for disease, img in disease_info
    ]

    return html.Div([
        # Conteneur principal
        html.Div([
            # Virus
            html.Div([
                html.Img(
                    src="https://raw.githubusercontent.com/badis2203/dash_board_projet_zitouni/main/src/image_dash/1_papilomavirus(1).png",
                    style=virus_animation_style['virus']
                )
            ], id='virus-container',
                style={**virus_animation_style['container-base'], **{'top': '50%', 'left': '50%'}}),

            # Images des maladies
            *disease_divs
        ], style={**virus_animation_style['main-container']}),

        dbc.Modal([
            dbc.ModalHeader(id="modal-header"),
            dbc.ModalBody(id="modal-body"),
            dbc.ModalFooter([
                html.Small("Source: De Sanjosé et al. (2019)", className="text-muted"),
                dbc.Button("Close", id="close-modal", className="ml-auto")
            ])
        ], id="info-modal")
    ])


def register_callbacks(app):
    @app.callback(
        [Output("info-modal", "is_open"),
         Output("modal-header", "children"),
         Output("modal-body", "children")],
        [Input(f"{disease}-container", "n_clicks") for disease in ['anus', 'oropharynx', 'penis', 'vagin']] +
        [Input("close-modal", "n_clicks")],
        [State("info-modal", "is_open")]
    )
    def toggle_modal(*args):
        ctx = dash.callback_context
        if not ctx.triggered:
            return False, "", ""

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger_id == "close-modal":
            return False, "", ""

        mapping = {
            "anus-container": ("Anus", "Anus"),
            "oropharynx-container": ("Upper Aerodigestive Tract", "Voies Aérodigestives Supérieures"),
            "penis-container": ("Penis", "Pénis"),
            "vagin-container": ("Female genital tract", "Vagin")
        }

        if trigger_id in mapping:
            title, key = mapping[trigger_id]
            content = html.Ul([html.Li(item) for item in info_mapping[key]])
            return True, title, content

        return False, "", ""

#CHARGEMENT DES DONNEES-----------------------------------------------

# Figure2
cancers = ["penis", "vulva", "larynx", "oropharynx", "col", "oral_cavite", "vagin", "anus"]
metrics = ["incidence", "mortalite"]

cancer_labels = {
    "penis": "Penis Cancer",
    "vulva": "Vulva Cancer",
    "larynx": "Laryngeal Cancer",
    "oropharynx": "Oropharyngeal Cancer",
    "col": "Cervical Cancer",
    "oral_cavite": "Oral Cavity Cancer",
    "vagin": "Vaginal Cancer",
    "anus": "Anal Cancer"
}

df_list = []
for cancer in cancers:
    for metric in metrics:
        file_path = f"https://raw.githubusercontent.com/badis2203/dash_board_projet_zitouni/main/data/2_cancers/2_{cancer}_{metric}.csv"
        df = pd.read_csv(file_path)
        df["Cancer"] = cancer
        df["Type"] = metric
        df_list.append(df)

df_cancer = pd.concat(df_list, ignore_index=True)
df_cancer["ASR (World)"] = pd.to_numeric(df_cancer["ASR (World)"], errors="coerce")
df_cancer["ASR (World)"].fillna(0, inplace=True)

# Figure3
df_hpv = pd.read_csv("https://raw.githubusercontent.com/badis2203/dash_board_projet_zitouni/main/data/3_HPV_vaccine_data.csv", sep=";",
                     skiprows=1)

iso_map = px.data.gapminder()[['country', 'iso_alpha']].drop_duplicates()
iso_map = dict(zip(iso_map.country, iso_map.iso_alpha))

def prepare_hpv_data(df):
    all_countries = pd.DataFrame({
        'Entity': list(iso_map.keys()),
        'Code': list(iso_map.values())
    })
    years = df['Year'].unique()
    complete_data = []

    for year in years:
        year_data = df[df['Year'] == year].copy()
        merged = all_countries.merge(year_data, on=['Entity', 'Code'], how='left')
        merged['Year'] = year
        merged['_3_b_1__sh_acs_hpv'] = merged['_3_b_1__sh_acs_hpv'].fillna(0)
        complete_data.append(merged)

    return pd.concat(complete_data, ignore_index=True)

df_hpv = prepare_hpv_data(df_hpv)

# Figure4
df_intro = pd.read_csv('https://raw.githubusercontent.com/badis2203/dash_board_projet_zitouni/main/data/introduction_hpv_vaccine.csv')
filtered_df_intro = df_intro[df_intro['intro__description_hpv__human_papilloma_virus__vaccine'] == 'Entire country']
filtered_df_intro.loc[:, 'Year'] = pd.to_numeric(filtered_df_intro['Year'], errors='coerce')
filtered_df_intro = filtered_df_intro.sort_values(by='Year')

countries_by_year = {}
for year in filtered_df_intro['Year'].unique():
    countries_by_year[year] = set(filtered_df_intro[filtered_df_intro['Year'] == year]['Entity'])

new_countries_by_year = {}
cumulative_countries = set()
cumulative_counts = []
for year in sorted(countries_by_year.keys()):
    new_countries_by_year[year] = countries_by_year[year] - cumulative_countries
    cumulative_countries.update(countries_by_year[year])
    cumulative_counts.append((year, len(cumulative_countries)))

cumulative_df = pd.DataFrame(cumulative_counts, columns=['Year', 'Total_Countries'])
min_year, max_year = cumulative_df['Year'].min(), cumulative_df['Year'].max()
country_options = [{'label': country, 'value': country} for country in sorted(filtered_df_intro['Entity'].unique())]

def create_layout(year_slider_id):
    return html.Div([
        dcc.Slider(id=year_slider_id, min=2000, max=2025, step=1, value=2010),
        html.H1("Données sur le depistage")
    ])

# Figure5
file_path_depistage = "https://raw.githubusercontent.com/badis2203/dash_board_projet_zitouni/main/data/5_france/depistage2023.csv"
df_depistage = pd.read_csv(file_path_depistage, sep=",")

df_depistage.columns = ['code_region', 'libelle_region', 'population', 'incidence', 'depistage_global',
                         'depistage_vingtaine', 'trentaine_trancheA', 'trentaine_trancheB',
                         'quarantaine_trancheA', 'quarantaine_trancheB', 'cinquantaine_trancheA',
                         'cinquantaine_trancheB', 'soixantaine']

corrections_regions = {
     "Paca": "Provence-Alpes-Côte d'Azur",
    "Ile de France": "Île-de-France",
    "Grand-Est": "Grand Est",
    "Bourgogne et Franche-Comté": "Bourgogne-Franche-Comté",
    "Centre": "Centre-Val de Loire",
    "Nouvelle Aquitaine": "Nouvelle-Aquitaine",
    "Auvergne et Rhône-Alpes": "Auvergne-Rhône-Alpes",
    "Corse": "Corse"
}

df_depistage['libelle_region'] = df_depistage['libelle_region'].replace(corrections_regions)

geojson_url = "https://france-geojson.gregoiredavid.fr/repo/regions.geojson"
geojson_data = requests.get(geojson_url).json()

def translate_geometry(geometry, delta_lon, delta_lat):
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

    current_dim = max(max_lon - min_lon, max_lat - min_lat)
    scale_factor = target_dim / current_dim if current_dim else 1

    scaled_geo = scale_geometry(geometry, scale_factor, center_lon, center_lat)
    min_lon2, max_lon2, min_lat2, max_lat2 = compute_bounding_box(scaled_geo)
    new_center_lon = (min_lon2 + max_lon2) / 2
    new_center_lat = (min_lat2 + max_lat2) / 2

    delta_lon = target_position[0] - new_center_lon
    delta_lat = target_position[1] - new_center_lat
    return translate_geometry(scaled_geo, delta_lon, delta_lat)

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
        feature["geometry"] = scale_and_translate_geometry(feature["geometry"],
                                                            target_dim,
                                                            target_positions[name])


# Figure6

file_path_filles = "https://raw.githubusercontent.com/badis2203/dash_board_projet_zitouni/main/data/6_donnees_vac_pap/6_couverture_vaccinale_2023_filles_nettoye.csv"
file_path_garcons = "https://raw.githubusercontent.com/badis2203/dash_board_projet_zitouni/main/data/6_donnees_vac_pap/6_couverture_vaccinale_2023_garcons_nettoye.csv"

df_filles = pd.read_csv(file_path_filles, sep=";")
df_garcons = pd.read_csv(file_path_garcons, sep=";")

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


df_filles_melted = df_filles.melt(id_vars=["Région"], var_name="Année", value_name="Vaccination Coverage")
df_garcons_melted = df_garcons.melt(id_vars=["Région"], var_name="Année", value_name="Vaccination Coverage")

for df_melt in [df_filles_melted, df_garcons_melted]:
    # Convert the year to an integer and add 16
    df_melt["Année"] = df_melt["Année"].astype(int) + 16

# APP DASH --------------------------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout de l'application
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from dash import callback_context
import os
app.layout = html.Div([
    # Colonne gauche (12%)
    html.Div([
        html.Ul([
            html.Li(html.A("CANCERS", href="#monde", className='nav-link',
                           **{'data-scroll': 'true'}, style={
                    'color': '#d6e1e7',
                    'textDecoration': 'none',
                    'fontSize': '120%',
                    'padding': '10px',
                    'display': 'block',
                    'cursor': 'pointer',
                    'whiteSpace': 'normal',
                    'wordWrap': 'break-word',
                    'overflowWrap': 'break-word',
                })),
            html.Hr(style={'width': '75%', 'margin': '10px auto', 'border': '1.5px solid #d6e1e7'}),

            html.Li(html.A("VACCINE", href="#vaccination", className='nav-link',
                           **{'data-scroll': 'true'}, style={
                    'color': '#d6e1e7',
                    'textDecoration': 'none',
                    'fontSize': '120%',
                    'padding': '10px',
                    'display': 'block',
                    'cursor': 'pointer',
                    'whiteSpace': 'normal',
                    'wordWrap': 'break-word',
                    'overflowWrap': 'break-word',
                })),
            html.Hr(style={'width': '75%', 'margin': '10px auto', 'border': '1.5px solid #d6e1e7'}),

            html.Li(html.A("ZOOM FRANCE", href="#zoom_france", className='nav-link',
                           **{'data-scroll': 'true'}, style={
                    'color': '#d6e1e7',
                    'textDecoration': 'none',
                    'fontSize': '120%',
                    'padding': '10px',
                    'display': 'block',
                    'cursor': 'pointer',
                    'whiteSpace': 'normal',
                    'wordWrap': 'break-word',
                    'overflowWrap': 'break-word',
                })),
        ], style={
            "listStyleType": "none",
            "padding": "0",
            "textAlign": "center",
            'marginTop': '12vh'
        })
    ], style={
        'width': '12%',
        'padding': '20px',
        'backgroundColor': '#457b9a',
        'height': '100vh',
        'position': 'fixed',
        'top': '0',
        'left': '0',
        'zIndex': '1000',
        'overflowY': 'auto'
    }),

    html.Div([
        # Colonne de droite (88%) - Contenu principal
        html.Div([
                html.H1("HPV Vaccination : A Global Public Health Challenge", className='dashboard-title',
                        style={'color': '#d6e1e7'})
            ], style={
                'top': 0,
                'backgroundColor': '#457b9a',
                'zIndex': 1000,
                'height': '45vh',
                "textAlign": "center",
                'fontSize':'50px'
            }),

        html.Div([
                # Première ligne de graphiques -----
                html.Section([
                    html.Div([
                        html.H2("Human papilllomavirus-related cancers", style={"textAlign": "center",'fontSize':'27px','color':'#0c425a'}),
                        html.Div(className='row-fixed', children=[create_virus_animation()],
                                 style={'height': '100%'}),

                    html.P(
                        "Click on a organ to see the attribution rate.",
                        style={
                            'textAlign': 'center',
                            'marginTop': '10px',
                            'fontSize': '14px',
                            'color': '#666'
                        }
                    ),
                    ], style={'width': '35%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'}),

                    html.Div([
                        html.H2("Cancer Map Analysis", style={"textAlign": "center",'fontSize':'27px','color':'#0c425a'}),
                        html.Div([
                            html.Div([
                                html.Label("Select a cancer type:"),
                                dcc.Dropdown(
                                    id="cancer-dropdown",
                                    options=[{"label": cancer_labels[c], "value": c} for c in
                                             df_cancer["Cancer"].unique()],
                                    value=df_cancer["Cancer"].unique()[0],
                                    clearable=False
                                ),
                            ], style={'width': '48%', 'paddingRight': '2%'}),
                            html.Div([
                                html.Label("Select an indicator:"),
                                dcc.RadioItems(
                                    id="type-radio",
                                    options=[
                                        {"label": "Incidence", "value": "incidence"},
                                        {"label": "Mortality", "value": "mortalite"}
                                    ],
                                    value="incidence",
                                    inline=True
                                ),
                            ], style={'width': '48%'}),
                        ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '10px'}),
                        dcc.Graph(id="map-choropleth", style = {'height':'60vh'})
                    ], style={'width': '65%', 'padding': '10px', 'display': 'flex', 'flexDirection': 'column'}),
                    # 50% de la largeur
                ], style={'display': 'flex', 'flexDirection': 'row','alignItems': 'center', 'height': '100vh', 'marginTop': '5vh','marginBottom':'15vh'},id="monde"),
            ], style={'display': 'flex'}),

            # Deuxième ligne de graphiques -----
            html.Section(
                [
                # colonne gauche (65%)
                html.Div([
                    html.H2("HPV Vaccination Analysis",
                            style={"textAlign": "center", 'marginTop': '10px', 'marginBottom': '10px','fontSize':'27px','color':'#0c425a'},id="vaccination"),
                    html.Div([
                        dcc.Slider(
                            id='year-slider',
                            min=int(df_hpv['Year'].min()),
                            max=int(df_hpv['Year'].max()),
                            value=2022,
                            marks={str(year): str(year) for year in sorted(df_hpv['Year'].unique())},
                            step=1
                        ),

                        html.Button("Play", id="play-button", n_clicks=0,
                                style={'marginLeft':'1.5vw'})
                    ], style={'marginBottom': '10px'}),
                    dcc.Interval(
                        id='interval-component',
                        interval=1000,
                        n_intervals=0,
                        disabled=True
                    ),

                    html.Div([
                        # Carte
                        html.Div([
                            dcc.Graph(id='choropleth-map-hpv',
                                      style={'height': '50vh', 'width': '120%', 'marginTop': '10px'})
                        ], style={'width': '100%', 'display': 'block', 'textAlign': 'left'}),

                        # Timeline
                        html.Div([
                            dcc.Graph(id='timeline-graph',
                                      style={'height': '30vh', 'width': '100%'})
                        ], style={'width': '100%', 'display': 'block'})

                    ], style={'width': '70%', 'margin': 'auto', 'display': 'block', 'textAlign': 'center'})
                ], style={'width': '65%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # colonne droite (35%)
                html.Div([
                    html.H2("Introduction",
                            style={"textAlign": "center", 'marginTop': '10px', 'marginBottom': '10px','fontSize':'27px','color':'#0c425a'}),
                    dcc.RangeSlider(
                        id='year-range-slider',
                        min=min_year,
                        max=max_year,
                        step=1,
                        marks={year: str(year) for year in range(min_year, max_year + 1, 2)},
                        value=[min_year, max_year],
                        allowCross=False
                    ),
                    dcc.Dropdown(
                        id='country-dropdown-intro',
                        options=country_options,
                        placeholder='Select a country...',
                        style={'marginBottom': '10px','marginTop': '10px'}
                    ),
                    # Graphique vaccination
                    dcc.Graph(id='vaccination-line-chart', style={'height': '55vh', 'width': '100%', 'marginTop': '0px'}),
                    html.Div(id='selected-country-list', style={'height': '17vh', 'overflowY': 'auto'})
                ], style={'width': '35%', 'display': 'inline-block', 'verticalAlign': 'top', 'overflow': 'hidden'})
            ], id='vaccination', style={'display': 'flex', 'max-height': '100vh'}),

            # Troisième ligne de graphiques -----
            html.Section([
                # carte dépistage (50%)
                html.Div([
                    html.H2("Incidence and Screening Rates by Region",
                            style={'textAlign': 'center', 'marginBottom': '10px','marginTop':'20px','fontSize':'27px','color':'#0c425a'},id="zoom_france"),
                    dcc.Dropdown(
                        id='age-group-dropdown',
                        options=[
                            {'label': 'Incidence', 'value': 'incidence'},
                            {'label': 'Global Screening', 'value': 'depistage_global'},
                            {'label': '25-29 years', 'value': 'depistage_vingtaine'},
                            {'label': '30-34 years', 'value': 'trentaine_trancheA'},
                            {'label': '35-39 years', 'value': 'trentaine_trancheB'},
                            {'label': '40-44 years', 'value': 'quarantaine_trancheA'},
                            {'label': '45-49 years', 'value': 'quarantaine_trancheB'},
                            {'label': '50-54 years', 'value': 'cinquantaine_trancheA'},
                            {'label': '55-59 years', 'value': 'cinquantaine_trancheB'},
                            {'label': '60-65 years', 'value': 'soixantaine'}

                        ],
                        value='depistage_global',
                        clearable=False,
                        style={'width': '90%', 'margin': '20px auto'}
                    ),
                    dcc.Graph(id="taux-depistage", style={'height': '45vh'})
                ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                # carte vacc (50%)
                html.Div([
                    html.H2("Vaccination Coverage at 16 Years old",
                            style={'textAlign': 'center', 'marginBottom': '10px','marginTop':'20px','fontSize':'27px','color':'#0c425a'}),
                    html.Div([
                        dcc.Dropdown(
                            id='sex-dropdown',
                            options=[
                                {'label': 'Girls', 'value': 'fille'},
                                {'label': 'Boys', 'value': 'garcon'}
                            ],
                            value='fille',
                            clearable=False,
                            style={'width': '45%', 'display': 'inline-block', 'marginRight': '10%'}
                        ),
                        dcc.Dropdown(
                            id='year-dropdown',
                            style={'width': '45%', 'display': 'inline-block'}
                        )
                    ], style={'margin': '20px'}),
                    dcc.Graph(id='map', style={'height': '55vh'}),
                    html.P(
                        "Click on a region to see the evolution.",
                        style={
                            'textAlign': 'center',
                            'marginTop': '10px',
                            'fontSize': '14px',
                            'color': '#666'
                        }
                    ),
                    html.Div(
                    html.Div(
                        [
                            # Bouton pour fermer la popup
                            html.Button(
                                "×",
                                id="close-popup",
                                style={
                                    'position': 'absolute',
                                    'top': '5px',
                                    'right': '5px',
                                    'background': 'none',
                                    'border': 'none',
                                    'fontSize': '20px',
                                    'cursor': 'pointer',
                                    'color': 'black'
                                }
                            ),
                            # Graphique dans la popup
                            dcc.Graph(
                                id='popup-graph',
                                style={'height': '40vh', 'width': '50vh'}
                            )
                        ],
                        id='popup',
                        style={
                            'display': 'none',
                            'position': 'fixed',
                            'top': '50%',
                            'left': '50%',
                            'transform': 'translate(-50%, -50%)',
                            'backgroundColor': 'white',
                            'padding': '10px',
                            'zIndex': '1000',
                            'width': '25%',
                            'height': '40%'
                        }
                    ))
                ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top',
                          'boxSizing': 'border-box', 'padding': '5px'})
            ], style={'display': 'flex', 'marginBottom': '165px', 'height': '100vh','marginTop':'15vh'})
    ], style={'width': '88%', 'display': 'flex', 'flexDirection': 'column', 'height': '100vh','marginLeft': '12%'})
], style={'display': 'flex', 'height': '100vh', 'margin': 0, 'padding': 0})

#LES CALLBACKs-----------------------------------------------------------

register_callbacks(app)

#2 graphe du monde
@app.callback(
    Output("map-choropleth", "figure"),
    [Input("cancer-dropdown", "value"),
     Input("type-radio", "value")]
)
def update_cancer_map(selected_cancer, selected_type):
    filtered_df = df_cancer[(df_cancer["Cancer"] == selected_cancer) & (df_cancer["Type"] == selected_type)]

    if filtered_df.empty:
        return px.choropleth(title="No data available")

    cancer_label = cancer_labels.get(selected_cancer, selected_cancer).capitalize()

    fig = px.choropleth(
        filtered_df,
        locations="Population",
        locationmode="country names",
        color="ASR (World)",
        hover_name="Population",
        title=f"{selected_type.capitalize()} of {cancer_label}",
        color_continuous_scale="Reds",
        projection="mercator"
    )

    fig.update_geos(
        showcoastlines=True,
        coastlinecolor="Black",
        showland=True,
        landcolor="white",
        projection_type="mercator",
        lonaxis=dict(showgrid=False, range=[-180, 180]),
        lataxis=dict(showgrid=False, range=[-35, 90])
    )

    fig.update_layout(
        margin={"r": 15, "t": 30, "l": 15, "b": 10},
    )


    return fig


# pour le troisème avec le monde
@app.callback(
    Output('choropleth-map-hpv', 'figure'),
    [Input('year-slider', 'value')]
)

def update_hpv_map(year):

    df_filtered = df_hpv[df_hpv['Year'] == year]

    if df_filtered.empty:
        return px.choropleth(title=f"No data available for Year {year}")

    # Création du graphique 3
    fig = px.choropleth(
        df_filtered,
        locations="Code",
        color="_3_b_1__sh_acs_hpv",
        hover_name="Entity",
        hover_data={"_3_b_1__sh_acs_hpv": True, "Code": False},
        labels={"_3_b_1__sh_acs_hpv": "Vaccination Rate (%)"},
        title=f"HPV Vaccination Rates for Girls (Year {year})",
        color_continuous_scale="Blues",
        range_color=[0, 100]

    )

    fig.update_geos(
        showcoastlines=True,
        coastlinecolor="Black",
        showland=True,
        landcolor="lightgray",
        projection_type="mercator",
        lonaxis=dict(showgrid=False, range=[-180, 180]),
        lataxis=dict(showgrid=False, range=[-35, 90])
    )

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                      "Vaccination Rate: %{z:.1f}%<extra></extra>"
    )

    fig.update_layout(
        margin={"r": 20, "t": 30, "l": 20, "b": 20},
        paper_bgcolor='white',
        geo=dict(
            bgcolor='white'
    ))

    return fig

@app.callback(
    Output('timeline-graph', 'figure'),
    [Input('year-slider', 'value')]
)
def update_timeline(year):
    df_grouped = df_hpv.groupby('Year')['_3_b_1__sh_acs_hpv'].mean().reset_index()

    fig = px.line(
        df_grouped,
        x='Year',
        y='_3_b_1__sh_acs_hpv',
        title="Global HPV Vaccination Rate Trends",
        labels={"_3_b_1__sh_acs_hpv": "Vaccination Rate (%)", "Year": "Year"},
        markers=True
    )

    fig.add_vline(x=year, line_dash="dash", line_color="red")

    fig.update_layout(
        margin={"r": 15, "t": 30, "l": 15, "b": 10},
    )

    return fig

@app.callback(
    Output('interval-component', 'disabled'),
    [Input('play-button', 'n_clicks')],
    [State('interval-component', 'disabled')]
)
def toggle_animation(n_clicks, is_disabled):
    return not is_disabled


@app.callback(
    Output('year-slider', 'value'),
    [Input('interval-component', 'n_intervals')],
    [State('year-slider', 'value')]
)
def animate_year(n_intervals, current_year):
    if current_year >= int(df_hpv['Year'].max()):
        return int(df_hpv['Year'].min())
    return current_year + 1


#Pour le quatrième introduction du vaccin dans le monde
@app.callback(
    Output('vaccination-line-chart', 'figure'),
    [Input('year-range-slider', 'value'),
     Input('country-dropdown-intro', 'value')]
)
def update_intro_chart(selected_year_range, selected_country):
    start_year, end_year = selected_year_range
    filtered_data = cumulative_df[(cumulative_df['Year'] >= start_year) & (cumulative_df['Year'] <= end_year)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_data['Year'],
        y=filtered_data['Total_Countries'],
        mode='lines+markers',
        name='Total countries',
        line=dict(color='lightblue', width=2),
        marker=dict(size=8, color='#2090c1'),
        showlegend = False
    ))

    if selected_country:
        country_data = filtered_df_intro[filtered_df_intro['Entity'] == selected_country]
        if not country_data.empty:
            intro_year = country_data['Year'].values[0]
            fig.add_trace(go.Scatter(
                x=[intro_year],
                y=[cumulative_df[cumulative_df['Year'] == intro_year]['Total_Countries'].values[0]],
                mode='markers',
                marker=dict(size=10, color='red'),
                name=f'{selected_country} introduced',
                showlegend = False
            ))

    fig.update_layout(
        title=f"Countries introducing HPV vaccination",
        xaxis_title="Year",
        yaxis_title="Total number of countries"
    )
    return fig

@app.callback(
    Output('selected-country-list', 'children'),
    [Input('vaccination-line-chart', 'clickData')]
)
def display_selected_countries(clickData):
    if clickData is None:
        return "Click on a point to see the list of new countries."

    selected_year = clickData['points'][0]['x']
    new_countries = new_countries_by_year.get(selected_year, set())
    if not new_countries:
        return f"No new countries introduced HPV vaccination in {selected_year}."
    return f"Year {selected_year}: {', '.join(sorted(new_countries))}"

#Pour le cinquième pour la france et le dépistage
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
        color_continuous_scale= "Blues",
        labels={
            selected_age_group: "Screening rate",
            "population": "Population",
            "incidence": "Incidence",
            "libelle_region":"Region name"
        }
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        resolution=50,
        showcountries=False,
        showcoastlines=False,
        showocean=False,
        projection_type="mercator"
    )

    fig.update_layout(
        dragmode="zoom",
        uirevision="fixed",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    return fig

# pour le 6eme pour la france

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
        range_color=[0, 60],
        mapbox_style="white-bg",
        zoom=3.0,
        center={"lat": 45.5, "lon": 4.5},
        opacity=0.85,
        hover_data=["Région", selected_year],
        labels={'Région':'Region', selected_year: "Vaccination coverage (%)"}
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
     Input('sex-dropdown', 'value'),
     Input('close-popup', 'n_clicks')],
    [State('popup', 'style')]
)
def update_popup_and_close(clickData, selected_sex, n_clicks, current_style):
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'close-popup':
        current_style['display'] = 'none'
        return go.Figure(), current_style

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
        y='Vaccination Coverage',
        title=f"Evolution in {region}",
        labels={'Année': 'Year', 'Vaccination Coverage': 'Percentage'}
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        title_font=dict(size=12),
        font=dict(size=10)
    )
    fig.update_yaxes(range=[0, 100])

    # Afficher la popup
    if current_style is None:
        current_style = {}
    current_style['display'] = 'block'
    return fig, current_style

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) 
    app.run_server(debug=True, host='0.0.0.0', port=port)
