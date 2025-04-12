# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Add a class_label column for better visualization (Success/Failure instead of 0/1)
spacex_df['class_label'] = spacex_df['class'].map({0: 'Failure', 1: 'Success'})

# Get unique launch sites for the dropdown
launch_sites = spacex_df['Launch Site'].unique().tolist()

# Create a dash application
app = dash.Dash(__name__)

# Create the app layout
app.layout = html.Div(children=[
    # Dashboard title
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show success/failure counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # TASK 3: Add a slider to select payload range
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 2000)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Add a scatter chart to show payload vs. launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback function for site-dropdown to update success-pie-chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Pie chart for all sites showing success vs. failure counts
        fig = px.pie(spacex_df, names='class_label', title='Launch Outcomes for All Sites')
    else:
        # Filter dataframe for the selected site and show success vs. failure
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(filtered_df, names='class_label', title=f'Launch Outcomes for {entered_site}')
    return fig

# TASK 4: Callback function for site-dropdown and payload-slider to update success-payload-scatter-chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    # Unpack the payload range
    low, high = payload_range
    # Filter dataframe based on payload range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    if entered_site == 'ALL':
        # Scatter plot for all sites within payload range
        fig = px.scatter(filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class_label', 
                         color='Booster Version', 
                         title='Payload vs. Launch Outcome for All Sites')
    else:
        # Further filter for the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class_label', 
                         color='Booster Version', 
                         title=f'Payload vs. Launch Outcome for {entered_site}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)