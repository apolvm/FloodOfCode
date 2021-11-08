# Import needed modules
import plotly.express as px
import plotly
import plotly.graph_objects as go
import pandas
import geopandas as gpd
import datetime
import json
import shapely
import numpy as np

# Need the latest version of plotly. Check with following
# print(plotly.__version__)

# Future proofing if we find easy way to add sattelite image
display_type = "open-street-map"

# Shape file data
# https://farisnatoursblog.wordpress.com/2021/03/31/mapping-and-shapefiles-with-plotly-graph_objs-and-geopandas/
# Get the shapefile into a geopandas
shapes = gpd.read_file('tl_2018_48201_roads.shp')

# Debug / understanding print
# print(shapes)

# JSON format the data
# json_dict = json.loads(shapes.tojson())

# Get the heatmap data
heatmap = pandas.read_csv('floodingheatmap12m.csv', sep='|')

# heatmap.rename(columns = {"Create Date":'createDate', "Closed Date":'closedDate'},inplace= "True")

# Slider data possibility and emulation
desiredDate = datetime.datetime(2021, 2, 18)

# tempDF = pandas.DataFrame()
# tempDF.loc[len(tempDF.index)] = heatmap.loc[0]

# for index, row in heatmap.iterrows():
# pos = heatmap[index]
# date1 = datetime.datetime(row.createDate[0:4],row.createDate[5:7], row.createDate[8:10])
# date2 = datetime.datetime(row.endDate[0:4],row.endDate[5:7], row.endDate[8:10])
# if date1 <= desiredDate:
#  if desiredDate <= date2:
#   tempDF.loc[len(tempDF.index)] = [20, 7, 5]


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

# FOR EACH LINESTRING ADD A SCATTERMAPBOX


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

# Update layout to have margin, a title, specified width, and certain display type.
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

##fig.show()

#---code for dash app
import dash
import dash_core_components as dcc
import dash_html_components as html


app = dash.Dash(__name__)

# layout

fig_names = [fig]
app.layout = html.Div([
    html.H1('Houston Flooding Data'),

    html.Div(id= 'output_container', children=[]),
    html.Br(),

    dcc.Graph(
        id='Houston',
        figure=fig
    ),
    dcc.Dropdown(id='layers',
                 options=[{'label': x, 'value': x} for x in fig_names],
                 value=None),
	# Charles' Type Selectors
    html.P("Type"),
    dcc.RadioItems(
	id='dispTypes',
	options=[{'label': 'Simple Map', 'value': 'open-street-map'},
		 {'label': 'Sattellite', 'value': 'other'}],
	value='open-street-map',
	labelStyle={'display':'inline-block'}
	),

    dcc.Slider(
        id='my_slider',
        min=1,
        max=12,
        value=10,
        marks={
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
        }
    )
])

#---------------------------------------------
@app.callback(
    [dash.dependencies.Output(component_id='output_container', component_property='children'),
     dash.dependencies.Output(component_id='Houston', component_property='figure')],
    [dash.dependencies.Input(component_id='my_slide', component_property='value'),
     dash.dependencies.Input(component_id='layers', component_property='value'),
     dash.dependencies.Input(component_id='dispTypes', component_property='value')]
)
def update_graph(option_selected):
    print(option_selected)
    print(type(option_selected))

def update_map(disptype):
    fig.update_layout(
    # mapbox_style=display_type,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    title='Houston Flooding'+str(disptype),
    width=500,
    height=500,
    mapbox={

        'style': disptype,
        'center': {'lat': 29.749907, 'lon': -95.358421},
        'zoom': 10}
)


if __name__ == '__main__':
    app.run_server(debug=True)
