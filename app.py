# Import needed modules
import plotly.express as px
import plotly
import pandas
import geopandas as gpd

# Need the latest version of plotly. Check with following
# print(plotly.__version__)

# Future proofing if we find easy way to add sattelite image
display_type = "open-street-map"

# Get the heatmap data
heatmap = pandas.read_csv('floodingheatmap12m.csv', sep='|')

# Create and show figure
fig = px.scatter_mapbox(
    lat=heatmap.lat,
    lon=heatmap.lon,

    hover_name=heatmap.Location,
    zoom=10,
    height=500,
    width=500,

)
fig.update_layout(
    mapbox_style=display_type,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    title='Houston Flooding',

)
#fig.show()

#---code for dash app
import dash
import dash_core_components as dcc
import dash_html_components as html


app = dash.Dash(__name__)

# layout

app.layout = html.Div([
    html.H1('Houston Flooding Data'),

    html.Div(id= 'output_container', children=[]),
    html.Br(),

    dcc.Graph(
        id='Houston',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)