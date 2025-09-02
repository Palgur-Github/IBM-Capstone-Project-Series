# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
#spacex_df = pd.read_csv("/Users/Balmund/Downloads/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36','font-size': 40}),
    # TASK 1: Add a Dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),
    # TASK 2: Add a pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    # TASK 3: Add a slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload, 
        max=max_payload, 
        step=1000,
        marks={int(min_payload): str(int(min_payload)),
               int((max_payload-min_payload)/4+min_payload): str(int((max_payload-min_payload)/4+min_payload)),
               int((max_payload-min_payload)/2+min_payload): str(int((max_payload-min_payload)/2+min_payload)),
               int((3*(max_payload-min_payload)/4)+min_payload): str(int((3*(max_payload-min_payload)/4)+min_payload)),
               int(max_payload): str(int(max_payload))
        },
        value=[min_payload, max_payload]
    ),
    html.Br(),
    # TASK 4: Add a scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])
# TASK 2: Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Group by site and sum successes (class==1)
        site_counts = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        site_counts.columns = ['Launch Site', 'Successes']
        fig = px.pie(
            site_counts,
            names='Launch Site',
            values='Successes',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count successes and failures, always show both
        success = (filtered_df['class'] == 1).sum()
        failure = (filtered_df['class'] == 0).sum()
        counts = pd.DataFrame({
            'Outcome': ['Success', 'Failure'],
            'Count': [success, failure]
        })
        fig = px.pie(
            counts,
            names='Outcome',
            values='Count',
            title=f'Success vs Failure for site {entered_site}'
        )
        return fig

# TASK 4: Callback for scatter chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites'
        )
        return fig
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for {entered_site}'
        )
        return fig
# Run the app
if __name__ == '__main__':
    app.run(debug=True)
