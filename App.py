import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px

import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div([ # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '25%',
            'height': '30px',
            'lineHeight': '30px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-div'),
    html.Div(id='output-datatable'),
])

#Saving the uploaded file into a dataframe.
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
# Creating the layout
    return html.Div([
        #html.H5(filename),
        #html.H6(datetime.datetime.fromtimestamp(date)),
        html.P("Select Plot Type"),
        dcc.Dropdown(id='Plot_type',
                    options=[{'label': 'scatterplot','value':'scatterplot'}, # This is the dropdown for Plot selection
                            {'label':'lineplot', 'value' : 'lineplot'},
                            {'label':'boxplot','value' : 'boxplot'},
                            {'label':'histogram','value' : 'histogram'},
                            ],
                            style={'width': '50%',
                                'height': '50px'},
                    clearable=True),
        html.P("GroupBy"),
        dcc.Dropdown(id='groupby',
                    options=[{'label':x, 'value':x} for x in df.columns],# This is the dropdown for Groupy selection
                            style={'width': '50%',
                                'height': '50px'},
                    clearable=True),   
        html.P("Aggregate"),
        dcc.Dropdown(id='aggregate',
                    options=[{'label': 'Minimum','value':'Minimum'},# This is  the dropdown for selceting aggregate function
                            {'label':'Maximum', 'value' :'Maximum'},
                            {'label':'Average','value' : 'Average'},
                            ],
                            style={'width': '50%',
                                'height': '50px'},
                            ) ,     
        html.P("Select X axis data"),      
        dcc.Dropdown(id='xaxis-data',
                    options=[{'label':x, 'value':x} for x in df.columns],# This is the dropdown for selecting data on X axis
                            style={'width': '50%',
                                'height': '50px'}),
        html.P("Select Y axis data"),
        dcc.Dropdown(id='yaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns], # This is  the dropdown for selecting data on Y axis
                            style={'width': '50%',
                                'height': '50px'}),
        html.Button(id="submit-button", children="Create Graph", # This is the button to trigger graph
                    style={'color':'#0074D9'}),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns], # This component is used to show data of the file on webpage
            page_size=15
        ),
        dcc.Store(id='stored-data', data=df.to_dict('records')), 
    ])


@app.callback(Output('output-datatable', 'children'), # This callback is used to display  data on the webpage
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(Output('output-div', 'children'), # This call back is used to plot the relevant graph
              Input('submit-button','n_clicks'),
              State('Plot_type','value'),
              State('stored-data','data'),
              State('xaxis-data','value'),
              State('yaxis-data', 'value'))
def make_graphs(n,plot_type,data, x_data, y_data):
    if n is None:
        return dash.no_update
    else:
        if plot_type == 'boxplot':
            bar_fig = px.box(data,x=x_data, y=y_data)
        elif plot_type == 'scatterplot':
            bar_fig = px.scatter(data, x=x_data, y=y_data)
        elif plot_type == 'lineplot':
            bar_fig = px.line(data,x=x_data, y=y_data)
        else :
            bar_fig = px.histogram(data,x=x_data, y=y_data,nbins=50) 
    return dcc.Graph(figure=bar_fig)

if __name__ == '__main__':
    app.run_server(debug=True)