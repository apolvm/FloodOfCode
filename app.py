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

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.FLATLY])
app.title = 'Dashboard'

# Future proofing if we find easy way to add sattelite image
display_type = "open-street-map"



app.layout = dbc.Container([ 

    dbc.Row(dbc.Col(html.H2("Houston Flooding Map"), width={'size': 12, 'offset': 0, 'order': 0}), 
    style = {'textAlign': 'center', 'paddingBottom': '1%'}),

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

@app.callback(
    Output(component_id='Houston', component_property='figure'),
    Input(component_id='my_slider', component_property='value')
)

def update_figure(month):
    month_internal = 0
    if month in [1,2,3,4,5,6]:
        month_internal = month+6
        year = 2020
    else: # month == 7 or 8 or 9 or 10 or 11 or 12 :
        month_internal = month-6
        year = 2021



    #print(str(month_internal)+' ' + str(year))
    # Get the shapefile into a geopandas
    shapes = gpd.read_file('tl_2018_48201_roads.shp')

    # Get the heatmap data
    heatmap = pandas.read_csv('floodingheatmap12m.csv', sep='|')

    heatmap['Create Date'] = pandas.to_datetime(heatmap['Create Date'])
    

    found = False
    
    #print(str(month) + "to" + str(month_internal))


    # Get the indexes of the flood events occuring in the selected month.



    
    # Heatmap data to a GeoDataFrame
    heatmap.rename(columns = {"Create Date":'createDate', "Closed Date":'closedDate'},inplace= "True")
    heatmap_gdf = gpd.GeoDataFrame(
    heatmap, geometry=gpd.points_from_xy(heatmap.lon, heatmap.lat))
    heatmap.createDate = pandas.to_datetime(heatmap.createDate)
    # Get it to right format
    heatmap_gdf = heatmap_gdf.set_crs('epsg:4326')

#    Get another copy of shapes (roads) before messing with it
    before_shapes = shapes.copy(deep=True)

        # Create a buffer on shapes.geometry
    shapes.geometry = shapes.buffer(.0002)
    heatmap_gdf['DFmonth']=heatmap_gdf.apply(lambda row: row.createDate.month, axis=1)
    heatmap_gdf['DFyear']=heatmap_gdf.apply(lambda row: row.createDate.year, axis=1)
    # Spatial join the roads gdf and the heatmap gdf 
    flooded_roads = gpd.sjoin(shapes,heatmap_gdf.loc[(heatmap_gdf.DFmonth== month_internal) & (heatmap_gdf.DFyear== year)],
                              'inner',predicate='contains')
    #flooded_roads = gpd.sjoin(shapes,heatmap_gdf,'inner',predicate='contains')
    print(flooded_roads.head())
    # Get all the indexes of roads that 

    fr_index = list(flooded_roads.index.values)
        
    # Future proofing if we find easy way to add sattelite image
    display_type = "open-street-map"

    # CREATE FIGURE AS SCATTER MAPBOX OF THE HEATMAP
    # https://plotly.com/python/lines-on-mapbox/
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

    for i in fr_index: #Change back to list(fr_index)
        feature= before_shapes.iloc[i].geometry
        name = before_shapes.iloc[i].FULLNAME
        #print(f"{feature} name {name}")
        # Prints poly gon and name
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
        #print(name)
        
        fig.add_trace(go.Scattermapbox(mode='lines',lat=lats, lon=lons, name=name,line=go.scattermapbox.Line(
        color = 'aqua',
        width = 5)))

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

    return fig

if __name__=='__main__':
    app.run_server(debug=True)
