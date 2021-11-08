from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from flask import Flask
import pandas as pd
import dash

import plotly.express as px
import plotly
import plotly.graph_objects as go
import pandas

import geopandas as gpd
import datetime
import json
import shapely
import numpy as np

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.FLATLY])
app.title = 'Dashboard'

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

app.layout = dbc.Container([ 

    dbc.Row(dbc.Col(html.H2("Houston Flooding Map"), width={'size': 12, 'offset': 0, 'order': 0}), style = {'textAlign': 'center', 'paddingBottom': '1%'}),

    dbc.Row(dbc.Col(dcc.Loading(children=[dcc.Graph(id='Houston', figure=fig),
                                          dcc.Slider(id='my_slider',min=1, max=12,value=10,marks={
            1: 'Jan',
            2: 'Feb',
            3: 'Mar',
            4: 'Apr',
            5: 'May',
            6: 'Jun',
            7: 'Jul',
            8: 'Aug',
            9: 'Sep',
            10: 'Oct',
            11: 'Nov',
            12: 'Dec'
        })
                                        ], color = '#000000', type = 'dot', fullscreen=True ) ))
])

@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='Houston', component_property='figure')],
    [Input(component_id='my_slider', component_property='value')]
)
def update_figure(selected_year):
    
    # Future proofing if we find easy way to add sattelite image
    display_type = "open-street-map"

    # CREATE FIGURE AS SCATTER MAPBOX OF THE HEATMAP
    # https://plotly.com/python/lines-on-mapbox/
    fig = go.Figure(go.Scattermapbox(
        # fig = go.Figure()
        # fig = px.scatter_mapbox( PUT THIS BACK TO WORK
        lat=heatmap.lat,
        lon=heatmap.lon,
        text=heatmap.Location,
        # hovertemplate = 'lon: %{lon} lat: %{lat} \n location: %{name}',
        # hover_name=heatmap.Location,
        # zoom=10,
        # height=500,
        # width = 500,

    ))
    for feature, name in zip(shapes.iloc[0:50].geometry,
                            shapes.iloc[0:50].FULLNAME):  # Possible issue of roads being the same in multiple areas?
        lats = []
        lons = []
        names = []
        if isinstance(feature, shapely.geometry.linestring.LineString):
            linestrings = [feature]
        elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
            linestrings = feature.geoms
        else:
            continue
        for linestring in linestrings:
            x, y = linestring.xy
            lats = np.append(lats, y)
            lons = np.append(lons, x)
            names = np.append(names, name)
            lats = np.append(lats, None)
            lons = np.append(lons, None)
            names = np.append(names, None)
        # https://plotly.github.io/plotly.py-docs/generated/plotly.graph_objects.Scattermapbox.html
    
    fig.add_trace(go.Scattermapbox(mode='lines', lat=lats, lon=lons, name=name))

    
    fig.update_layout(
        # mapbox_style=display_type,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title='Houston Flooding',
        width=500,
        height=500,
        mapbox={
            'style': display_type,
            'center': {'lat': 29.749907, 'lon': -95.358421},
            'zoom': 10}
    )

    return fig

if __name__=='__main__':
    app.run_server(debug=True)
