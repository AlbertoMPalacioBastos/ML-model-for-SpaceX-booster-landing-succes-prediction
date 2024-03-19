# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Dash application
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # Dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                     {'label': 'All Sites', 'value': 'ALL'},
                                                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                     {'label': 'KSC LC-39A', 'value':'KSC LC-39A'},
                                                     {'label': 'CCAFS SLC-40', 'value':'CCAFS SLC-40'}
                                                     ],
                                                 value='ALL',
                                                 placeholder="place holder here",
                                                 searchable=True
                                            ),
                                html.Br(),

                                # Pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site                        
                                html.Div(dcc.Graph(id='success-pie-chart')),                                
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # Slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=100,
                                                marks={key:str(key) for key in range(0,11000,1000)},
                                                value=[min_payload, max_payload]),

                                # Scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart'))
                               ]
                     )

# Callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, 
                     values='class',
                     names='Launch Site',
                     title='Total success launches by site')
        return fig
    else:
        mask = (spacex_df['Launch Site'] == entered_site)
        filtered_df = spacex_df[mask]
        fig = px.pie(filtered_df, 
                     values='class',
                     names='class',
                     title='Total success launches for site ' + entered_site)
        return fig

# Callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
               Input(component_id="payload-slider", component_property="value")])

def get_scatter_chart(entered_site, slider_range):
    if entered_site == 'ALL':
        low, high = slider_range
        mask = ((spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high))
        filtered_df = spacex_df[mask]
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for all Sites')
        return fig
    else:  
        low, high = slider_range
        mask1 = (spacex_df['Launch Site'] == entered_site)
        mask2 = ((spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high))
        filtered_df = spacex_df[mask1 & mask2]
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for Site ' + entered_site)
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()