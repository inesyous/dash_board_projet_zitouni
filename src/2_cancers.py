import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Liste des cancers et des métriques
cancers = ["penis", "vulva", "larynx", "oropharynx", "col", "oral_cavite", "vagin", "anus"]
metrics = ["incidence", "mortalite"]

# Créer un dictionnaire pour associer un nom à un type de cancer
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
        file_path = f"/Users/perrine/Desktop/M1/monde/2_{cancer}_{metric}.csv"
        df = pd.read_csv(file_path)
        df["Cancer"] = cancer
        df["Type"] = metric
        df_list.append(df)

df = pd.concat(df_list, ignore_index=True)

# Conversion de la colonne "ASR (World)" en numérique
df["ASR (World)"] = pd.to_numeric(df["ASR (World)"], errors="coerce")
df["ASR (World)"].fillna(0, inplace=True)


app = dash.Dash(__name__)

# Layout de l'application
app.layout = html.Div([
    html.H1("Interactive Map of Human Papillomavirus and Associated Cancers", style={"textAlign": "center"}),


    html.Div([
        # Sélecteur pour le type de cancer
        # Sélecteur pour le type de cancer
        html.Div([
            html.Label("Select a cancer type:"),
            dcc.Dropdown(
                id="cancer-dropdown",
                options=[{"label": cancer_labels[c], "value": c} for c in df["Cancer"].unique()],
                value=df["Cancer"].unique()[0],
                clearable=False
            ),
        ], style={'width': '48%', 'paddingRight': '2%'}),  # Espace entre les deux éléments

        # Sélecteur pour l'indicateur
        html.Div([
            html.Label("Select an indicator:"),
            dcc.RadioItems(
                id="type-radio",
                options=[
                    {"label": "Incidence", "value": "incidence"},
                    {"label": "Mortality", "value": "mortality"}
                ],
                value="incidence",  # valeur par défaut
                inline=True
            ),
        ], style={'width': '48%'}),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '10px'}),  # Flexbox pour disposition côte à côte

    # Graphique de la carte choroplèthe
    dcc.Graph(id="map-choropleth")
])


# Callback qui va mettre à jour la carte en fonction des sélections
@app.callback(
    Output("map-choropleth", "figure"),
    [Input("cancer-dropdown", "value"),
     Input("type-radio", "value")]
)
def update_map(selected_cancer, selected_type):
    # Filtrage des données en fonction des sélections
    filtered_df = df[(df["Cancer"] == selected_cancer) & (df["Type"] == selected_type)]

    if filtered_df.empty:
        return px.choropleth(title="No data available")

    cancer_label = cancer_labels.get(selected_cancer, selected_cancer).capitalize()

    # Création du graphique choroplèthe
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

    # Configuration géographique de la carte
    fig.update_geos(
        showcoastlines=True,
        coastlinecolor="Black",
        showland=True,
        landcolor="white",
        projection_type="mercator",
        lonaxis=dict(showgrid=True, range=[-180, 180]),
        lataxis=dict(showgrid=True, range=[-35, 90])
    )

    # Mise en forme du graphique
    fig.update_layout(
        geo=dict(showcoastlines=True),
        height=600,
        width=1000,
        margin={"r": 20, "t": 40, "l": 20, "b": 20}
    )

    return fig
    
if __name__ == "__main__":
    app.run_server(debug=True)
