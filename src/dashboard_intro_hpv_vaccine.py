import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

# Charger les données depuis le fichier CSV
df = pd.read_csv('introduction_hpv_vaccine.csv')

# Filtrer les données pour les pays où la vaccination est introduite dans tout le pays
filtered_df = df[df['intro__description_hpv__human_papilloma_virus__vaccine'] == 'Entire country']
filtered_df['Year'] = pd.to_numeric(filtered_df['Year'], errors='coerce')
filtered_df = filtered_df.sort_values(by='Year')

# Créer un dictionnaire pour stocker les pays ayant introduit la vaccination chaque année
countries_by_year = {}
for year in filtered_df['Year'].unique():
    countries_by_year[year] = set(filtered_df[filtered_df['Year'] == year]['Entity'])

new_countries_by_year = {}
cumulative_countries = set()
cumulative_counts = []
for year in sorted(countries_by_year.keys()):
    new_countries_by_year[year] = countries_by_year[year] - cumulative_countries
    cumulative_countries.update(countries_by_year[year])
    cumulative_counts.append((year, len(cumulative_countries)))

cumulative_df = pd.DataFrame(cumulative_counts, columns=['Year', 'Total_Countries'])
min_year, max_year = cumulative_df['Year'].min(), cumulative_df['Year'].max()

# Liste des pays uniques
country_options = [{'label': country, 'value': country} for country in sorted(filtered_df['Entity'].unique())]

# Initialisation de l'application Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Total countries introducing HPV vaccination by year"),

    dcc.RangeSlider(
        id='year-slider',
        min=min_year,
        max=max_year,
        step=1,
        marks={year: str(year) for year in range(min_year, max_year + 1, 2)},
        value=[min_year, max_year],
        allowCross=False
    ),

    dcc.Dropdown(
        id='country-dropdown',
        options=country_options,
        placeholder='Select a country...',
        style={'marginBottom': '20px'}
    ),

    html.Div([  # Conteneur principal en flexbox
        # Colonne pour le graphique (2/3 de la largeur)
        html.Div([
            dcc.Graph(id='vaccination-line-chart', style={'width': '100%'})
        ], style={'flex': 2}),  # Le graphique prend 2 parts sur 3

        # Colonne pour la liste des pays (1/3 de la largeur)
        html.Div([
            html.H3("New countries that introduced HPV vaccination in the selected year:"),
            html.Div(id='selected-country-list', style={'whiteSpace': 'pre-line', 'fontSize': '16px'})
        ], style={'flex': 1, 'paddingLeft': '20px', 'marginTop': '50px'})  # La liste prend 1 part sur 3

    ], style={'display': 'flex', 'flexDirection': 'row'})  # Disposition en ligne (flexbox)
])

# Callback pour mettre à jour le graphique
@app.callback(
    Output('vaccination-line-chart', 'figure'),
    [Input('year-slider', 'value'), Input('country-dropdown', 'value')]
)
def update_chart(selected_year_range, selected_country):
    start_year, end_year = selected_year_range
    filtered_data = cumulative_df[(cumulative_df['Year'] >= start_year) & (cumulative_df['Year'] <= end_year)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_data['Year'],
        y=filtered_data['Total_Countries'],
        mode='lines+markers',
        name='Total countries',
        line=dict(color='lightblue', width=2),
        marker=dict(size=8, color='#2090c1')
    ))

    if selected_country:
        country_data = filtered_df[filtered_df['Entity'] == selected_country]
        if not country_data.empty:
            intro_year = country_data['Year'].values[0]
            fig.add_trace(go.Scatter(
                x=[intro_year],
                y=[cumulative_df[cumulative_df['Year'] == intro_year]['Total_Countries'].values[0]],
                mode='markers',
                marker=dict(size=10, color='red'),
                name=f'{selected_country} introduced'
            ))

    fig.update_layout(
        title=f"Total countries introducing HPV vaccination ({start_year} - {end_year})",
        xaxis_title="Year",
        yaxis_title="Total number of countries"
    )
    return fig

# Callback pour afficher la liste des nouveaux pays lorsqu'on clique sur un point
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

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
