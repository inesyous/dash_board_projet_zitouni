import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px

# Charger le fichier CSV
df = pd.read_csv("/Users/perrine/Desktop/M1/S2/modelisation/HPV_vaccine_data.csv", sep=";", skiprows=1)

# Créer un dictionnaire de correspondance pays-code ISO
iso_map = px.data.gapminder()[['country', 'iso_alpha']].drop_duplicates()
iso_map = dict(zip(iso_map.country, iso_map.iso_alpha))


# Préparer les données
def prepare_data(df):
    # Obtenir tous les codes ISO uniques de Plotly
    all_countries = pd.DataFrame({
        'Entity': list(iso_map.keys()),
        'Code': list(iso_map.values())
    })

    # Pour chaque année, fusionner avec la liste complète des pays
    years = df['Year'].unique()
    complete_data = []

    for year in years:
        year_data = df[df['Year'] == year].copy()
        # Fusionner avec tous les pays
        merged = all_countries.merge(year_data, on=['Entity', 'Code'], how='left')
        # Remplir l'année pour les pays manquants
        merged['Year'] = year
        # Remplir les valeurs manquantes avec 0
        merged['_3_b_1__sh_acs_hpv'] = merged['_3_b_1__sh_acs_hpv'].fillna(0)
        complete_data.append(merged)

    return pd.concat(complete_data, ignore_index=True)


df = prepare_data(df)

# Appli Dash
app = dash.Dash(__name__)

# Mise en page du Dashboard
app.layout = html.Div([
    html.H1("HPV Vaccination Rates for Girls Worldwide"),

    html.Div([
        dcc.Slider(
            id='year-slider',
            min=int(df['Year'].min()),
            max=int(df['Year'].max()),
            value=2022,
            marks={str(year): str(year) for year in sorted(df['Year'].unique())},
            step=1
        ),
        html.Button("Play", id="play-button", n_clicks=0)
    ], style={'marginBottom': '20px'}),

    dcc.Interval(
        id='interval-component',
        interval=1000,
        n_intervals=0,
        disabled=True
    ),

    dcc.Graph(id='choropleth-map'),
    dcc.Graph(id='timeline-graph')
])


@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('year-slider', 'value')]
)
def update_choropleth(year):
    df_filtered = df[df['Year'] == year]

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

    # Mise à jour de l'apparence de la carte
    fig.update_geos(
        showframe=True,  # Show frame
        framecolor="black",
        showcoastlines=True,
        coastlinecolor="black",
        showland=True,
        landcolor="lightgray",  # More visible color for countries without data
        showcountries=True,
        countrycolor="black",
        countrywidth=0.5,
        projection_type="equirectangular"
    )

    # Personnalisation du hover
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                      "Vaccination Rate: %{z:.1f}%<extra></extra>"
    )

    fig.update_layout(
        height=600,
        width=1100,
        margin={"r": 0, "t": 40, "l": 0, "b": 20},
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig


@app.callback(
    Output('timeline-graph', 'figure'),
    [Input('year-slider', 'value')]
)
def update_timeline(year):
    df_grouped = df.groupby('Year')['_3_b_1__sh_acs_hpv'].mean().reset_index()

    fig = px.line(
        df_grouped,
        x='Year',
        y='_3_b_1__sh_acs_hpv',
        title="Global HPV Vaccination Rate Trends",
        labels={"_3_b_1__sh_acs_hpv": "Average Vaccination Rate (%)", "Year": "Year"},
        markers=True
    )

    fig.add_vline(x=year, line_dash="dash", line_color="red")

    fig.update_layout(
        height=400,
        margin={"r": 20, "t": 40, "l": 20, "b": 20},
        hovermode='x unified'
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
    if current_year >= int(df['Year'].max()):
        return int(df['Year'].min())
    return current_year + 1

if __name__ == "__main__":
    app.run_server(debug=True)
