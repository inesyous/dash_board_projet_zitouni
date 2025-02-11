import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

# Load data from the CSV file
df = pd.read_csv('introduction_hpv_vaccine.csv')

# Filter data for countries where vaccination was introduced nationwide
filtered_df = df[df['intro__description_hpv__human_papilloma_virus__vaccine'] == 'Entire country']
filtered_df['Year'] = pd.to_numeric(filtered_df['Year'], errors='coerce')
filtered_df = filtered_df.sort_values(by='Year')

# Create a dictionary to store countries that introduced vaccination each year
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

# List of unique countries
country_options = [{'label': country, 'value': country} for country in sorted(filtered_df['Entity'].unique())]

# Initialize Dash application
app = dash.Dash(__name__)

# Create layout function
def create_layout():
    return html.Div([
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

        html.Div([  # Main flexbox container
            # Column for the chart (2/3 width)
            html.Div([
                dcc.Graph(id='vaccination-line-chart', style={'width': '100%'})
            ], style={'flex': 2}),  # Chart takes 2 out of 3 parts

            # Column for the list of countries (1/3 width)
            html.Div([
                html.H3("New countries that introduced HPV vaccination in the selected year:"),
                html.Div(id='selected-country-list', style={'whiteSpace': 'pre-line', 'fontSize': '16px'})
            ], style={'flex': 1, 'paddingLeft': '20px', 'marginTop': '50px'})  # List takes 1 out of 3 parts

        ], style={'display': 'flex', 'flexDirection': 'row'})  # Row layout (flexbox)
    ])

# Callback to update the chart
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

# Callback to display the list of new countries when clicking on a point
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

# Run the application
if __name__ == '__main__':
    app.layout = create_layout()  # Set the layout to the create_layout() function
    app.run_server(debug=True)
