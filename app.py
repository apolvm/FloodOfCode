# Team FloodOfCode's code for HPC in the City: St. Louis 2021 submission
# Program completed by:
# Dash App Code - AnaPatricia Olvera
# Map Display Code - Charles Gaffney
# Design Outline - Tyler Jackson

# Google Cloud and Deploying Debugging - Cole McKnight and Dr. William Mobley
# Map Display Coding Guidance and Help - Dr. William Mobley


# Import the modules needed 
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
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
# Create the Server and App
server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.FLATLY])
app.title = 'Dashboard'

# Future proofing if we find easy way to add sattelite image
display_type = "open-street-map"


# Define the app's layout
app.layout = dbc.Container([ 
    # Create a heading for the app
    dbc.Row(dbc.Col(html.H2("Houston Flooding Map"), width={'size': 12, 'offset': 0, 'order': 0}), 
    style = {'textAlign': 'center', 'paddingBottom': '1%'}),
    # Create the Graph and Slider
    # Slider max value set to 12 and min value set to 1 to fit 12 months in a year.
    # Values could be reordered to fit the order a dataset requires
    # The months start with July due to the dataset we use only covering Jul 2020 to Jun 2021
    dbc.Row(dbc.Col(dcc.Loading(children=[dcc.Graph(id='Houston'),
                                          dcc.Slider(id='my_slider',min=1, max=12,value=8,
                                          marks={
                                              1:'Jul 2020',
                                              2:'Aug',
                                              3: 'Sept',
                                              4: 'Oct',
                                              5: 'Nov',
                                              6: 'Dec',
                                              7: 'Jan',
                                              8: 'Feb',
                                              9: 'Mar',
                                              10: 'Apr',
                                              11: 'May',
                                              12: 'Jun 2021',
                                              })
                                        ], color = '#000000', type = 'dot', fullscreen=True ) ))
])
# Process the app's output and input.
@app.callback(
    Output(component_id='Houston', component_property='figure'),
    Input(component_id='my_slider', component_property='value')
)
# Runs code to display the figure (map). A integer is passed as the month to sort what flood events are displayed
def update_figure(month):
    # Declare a variable for month that does not try changing the received input
    month_internal = 0
    # Due to the data the dataset contains, for the first 6 month value possibilities.
    # Set month_internal to 6 added to the month value from the slider and set the year to 2020
    if month in [1,2,3,4,5,6]:
        month_internal = month+6
        year = 2020
    # For the other month values, subtract 6 and set the year to 2021
    else: # month == 7 or 8 or 9 or 10 or 11 or 12 :
        month_internal = month-6
        year = 2021



    #print(str(month_internal)+' ' + str(year))
    # Get the shapefile into a geopandas
    shapes = gpd.read_file('tl_2018_48201_roads.shp')

    # Get the heatmap data
    heatmap = pandas.read_csv('floodingheatmap12m.csv', sep='|')
    # Make sure values in 'Create Date' column are in datetime
    heatmap['Create Date'] = pandas.to_datetime(heatmap['Create Date'])
    

    found = False
    
    #print(str(month) + "to" + str(month_internal))


    



    
    # Heatmap data to a GeoDataFrame
    heatmap.rename(columns = {"Create Date":'createDate', "Closed Date":'closedDate'},inplace= "True")
    heatmap_gdf = gpd.GeoDataFrame(
    heatmap, geometry=gpd.points_from_xy(heatmap.lon, heatmap.lat))
    heatmap.createDate = pandas.to_datetime(heatmap.createDate)
    # Get it to right format
    heatmap_gdf = heatmap_gdf.set_crs('epsg:4326')

#    Get another copy of shapes (roads) before using it
    before_shapes = shapes.copy(deep=True)

    # Create a buffer on shapes.geometry
    shapes.geometry = shapes.buffer(.0002)
    # Add month and year columns to the GeoDataFrame
    heatmap_gdf['DFmonth']=heatmap_gdf.apply(lambda row: row.createDate.month, axis=1)
    heatmap_gdf['DFyear']=heatmap_gdf.apply(lambda row: row.createDate.year, axis=1)
    # Spatial join the roads gdf with the points from the heatmap that are specifically from the requested month and year
    flooded_roads = gpd.sjoin(shapes,heatmap_gdf.loc[(heatmap_gdf.DFmonth== month_internal) & (heatmap_gdf.DFyear== year)],
                              'inner',predicate='contains')
    #flooded_roads = gpd.sjoin(shapes,heatmap_gdf,'inner',predicate='contains')
    print(flooded_roads.head())
    # Get all the indexes of roads that 

    fr_index = list(flooded_roads.index.values)
        
    # Future proofing if we find easy way to add sattelite image
    display_type = "open-street-map"

    # Create the Scattermapbox of all the flood event points from the requested time period found in heatmap_gdf
    
    fig=go.Figure(go.Scattermapbox(
                    lat=heatmap.loc[(heatmap_gdf.DFmonth== month_internal) & (heatmap_gdf.DFyear== year)].lat,
                    lon=heatmap.loc[(heatmap_gdf.DFmonth== month_internal) & (heatmap_gdf.DFyear== year)].lon,
                    text=heatmap.loc[(heatmap_gdf.DFmonth== month_internal) & (heatmap_gdf.DFyear== year)].Location,
                    marker=go.scattermapbox.Marker(
                    size=10
                    ),
                    hoverlabel=go.scattermapbox.Hoverlabel(
                        bgcolor='darkslateblue',
                        bordercolor='lightgrey'
                    )))
    # Draw each flooded road
    for i in fr_index: #Change back to list(fr_index)
        # Get the shape and name of each road
        feature= before_shapes.iloc[i].geometry
        name = before_shapes.iloc[i].FULLNAME
        #print(f"{feature} name {name}")
        # Create needed empty lists
        lats = []
        lons = []
        names = []
        
        # Check to see what type of geometry each shape is and store data based on the type
        if isinstance(feature, shapely.geometry.linestring.LineString):
            linestrings = [feature]
        elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
            linestrings = feature.geoms
        else:
            continue
        # For each linestring, grab everything that is needed to add the trace of it.
        for linestring in linestrings:
            x, y = linestring.xy
            lats = np.append(lats, y)
            lons = np.append(lons, x)
            names = np.append(names, name)
            lats = np.append(lats, None)
            lons = np.append(lons, None)
            names = np.append(names, None)
        
        #print(name)
        # Add the flooded roads to the map display
        fig.add_trace(go.Scattermapbox(mode='lines',lat=lats, lon=lons, name=name,line=go.scattermapbox.Line(
        color = 'aqua',
        width = 5)))
    # Final updates to the display
    fig.update_layout(
        # mapbox_style=display_type,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title='Houston Flooding',
        width=800,
        height=600,
        mapbox={
            'style': 'open-street-map',
            'center': {'lat': 29.749907, 'lon': -95.358421},
            'zoom': 10}
    )
    # Return the figure
    return fig
# Only run the program if this file in particular is being run
if __name__=='__main__':
    app.run_server(debug=True)
