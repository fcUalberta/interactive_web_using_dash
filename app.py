# Importing libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from plotly.subplots import make_subplots
import dash_table

from utils import create_polar, create_pairwise, create_gauge


# Reading data in as DataFrame
dfJoined = pd.read_csv("shap.csv", sep='\t')
# Copy selected columns
df = dfJoined[["sepal length (cm)_shap", "sepal width (cm)_shap", "petal length (cm)_shap", "petal width (cm)_shap","shift","target"]]

# Storing required column names
axes =["sepal length", "sepal width", "petal length", "petal width"]

# Renaming the column names for ease of reading
mapping1 = {dfJoined.columns[1]:axes[0], dfJoined.columns[3]: axes[1], dfJoined.columns[5]:axes[2], dfJoined.columns[7]:axes[3]}
mapping2 = {df.columns[0]:axes[0], df.columns[1]: axes[1], df.columns[2]:axes[2], df.columns[3]:axes[3]}
dfJoined = dfJoined.rename(columns=mapping1)
df=df.rename(columns=mapping2)

# Rounding of decimals to standardize
df=df.round(decimals=2)
dfJoined=dfJoined.round(decimals=2)



# Creating a new DF with shap values in the positive range
df_norm=df+max(abs(df.min()))
df_norm['shift'] = dfJoined['shift']
df_norm['target'] = dfJoined['target']


filtered_df = df_norm[df_norm['target']==0]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Setting some group styling

colors = {
    'background': '#FFE6E6',
    'bg': '#DCF3FF',
    'text': '#1087C8'
}
tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#F97A7A',
    'color': 'white',
    'padding': '6px'
}
graph_style = {
'borderTop': '1px solid #d6d6d6',
'borderBottom': '1px solid #d6d6d6',
'padding': '2px',
'display': 'inline-block',
'box-shadow': '3px 3px 3px 3px lightgrey',
'padding-top':'2px',
'float':'center',
'backgroundColor':colors['background'],
'plot_bgcolor': colors['background']

}
chart_box = {
  'box-shadow': '3px 3px 3px 3px lightgrey',
  'padding-top':'2px',"width": "900px",
  "margin": "0 auto",
  'backgroundColor':colors['background'],
  'plot_bgcolor': colors['background']
}
target_options = []

# Storing the class names based on class numbers 0 or 1
for cls in range(0,2):
    if cls == 0:
        target_options.append({'label':'Class Not Versicolor','value':cls})
    else:
        target_options.append({'label':'Class Versicolor','value':cls})


# Initializing fig
fig = make_subplots(rows=1,cols=2,shared_yaxes= True,
                    specs=[[{'type': 'polar'}]*2],
                     subplot_titles=("Selected Record","Represented Class"))


# Creating pairwise plot as its not dependent on callbacks
fig5 = create_pairwise()


# website layout
app.layout = html.Div([

    html.H2("Interactive Data Driven Visualization Dashboard", style={'text-align':'center','font-family':'sans-serif'}),

    # All tabs
    dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
        # Tab 1
        dcc.Tab(label='Class-specific Multi-Attribute Comparison', value='tab-1', style=tab_style,
        selected_style=tab_selected_style, children = [
        html.Div([
            # Div for Dropdown and H3
            html.Div([
            html.Div([],className="b-container"),
            html.H6(
                'Select a class from the dropdown to view Class-specific behaviour of petals and sepals'
            ,style={'text-align':'center','font-family':'sans-serif', 'color': colors['text']}),
            dcc.Dropdown(id='class-picker',options=target_options,
            value = dfJoined['target'].max(), style={'width':'100%', 'text-align':'center', 'color':colors["text"]})
            ],  className = "container"),

            # Adding vertical space
            html.Div([],className="b-container"),
            # Div for graph 1 - Box plot
            html.Div([

                dcc.Graph(
                    id='graph1')
            ], style= graph_style,className="five columns"),

            # Div for graph 2 - Bubble Chart
            html.Div([
                dcc.Graph(
                    id='graph2')
            ],style=graph_style, className="five columns")

        ], style = {"textAlign":"center"},className="row")

        ]),

        # Tab 2
        dcc.Tab(label='Pair-wise Attribute Comparison of Universe', value='tab-2', style=tab_style,
        selected_style=tab_selected_style, children = [
        html.Div([


            # Adding vertical space
            html.Div([],className="b-container"),
            # Div for graph - Scatter Matrix
            html.Div([
                html.H6(
                    'Comparison of pair-wise interaction between the attributes for each class'
                ,style={'text-align':'center','font-family':'sans-serif'}),
                dcc.Graph(
                    id='graph5',figure = fig5)
            ], style= chart_box)
        ], className="row")

        ]),
        # Tab 3
        dcc.Tab(label='Instance-specific Multi-Attribute Comparison', value='tab-3', style=tab_style,
        selected_style=tab_selected_style, children=[
        html.Div([
            # Div for vertical space
            html.Div([],className="b-container"),
            # Div for Input
            html.Div([
            html.H6(
                'Enter the record number between 0 and 37 you would like to visualize and compare'
            ,style={'font-family':'sans-serif', 'text-align':'center','color':colors["text"]},),
            html.Div([
            dcc.Input(id='row-picker', value=0, type="number",
            debounce=False,min=0,max=37, placeholder="Enter below 37 ",
            style = {"width":"100%", "text-align":'center','color':colors["text"]})
            ]),
            html.Div(id="class_display",style = {"width":"100%", "text-align":'center','color':colors["text"]})
            ], className = "container"),
        # Div for vertical space
        html.Div([],className="b-container"),
        # Div for Polar chart
        html.Div([
            dcc.Graph(
                id='graph3',figure=fig)
            ], style=graph_style,className="five columns"),

        # Div for Gauge chart
        html.Div([
            html.H6("Selected Record Vs Represented Class Single-Attribute Comparison"
            ,style={'text-align':'center','font-family':'sans-serif'}),
            dcc.Graph(
                id='graph4',figure=fig)
            ], style=graph_style,className="six columns")


        ], className = "row")

        ])

        ], style=tabs_styles)


])

# Callback for Tab 1 Graph 1
@app.callback(Output('graph1','figure'),
        [Input('class-picker','value')])
def update_figure(selected_class):
    """
    Function to update the graph based on selected class
    Arguments:
        selected_class: class selected as integer
    Returns:
        Updated box plot object

    """
    filtered_df = dfJoined[dfJoined['target']==selected_class]
    filtered_df2 = df_norm[df_norm['target']==selected_class]

    #axes =["sepal length (cm)_shap", "sepal width (cm)_shap", "petal length (cm)_shap", "petal width (cm)_shap"]

    traces=[]


    #print(filtered_df.head())
    for axis in axes:
        [traces.append(go.Box(
            #x=filtered_df['shift'],
            y=filtered_df[axis],
            name=axis
            ))]



    return {'data':traces,
                'layout':go.Layout(title='Class-specific Comparison between Attributes (Box Plot)',
                                    #xaxis={'title':'Shift'},
                                    yaxis={'title':'Sepal and Petal attributes'},
                                        hovermode='closest',
                                        paper_bgcolor='rgba(233,233,233,0)',
                                        plot_bgcolor='rgba(255,233,0,0)')}

# Callback for Tab 1 Graph 2
@app.callback(Output('graph2','figure'),
        [Input('class-picker','value')])
def update_figure(selected_class):
    """
    Function to update the graph based on selected class
    Arguments:
        selected_class: class selected as integer
    Returns:
        Updated Bubble chart object

    """

    filtered_df = dfJoined[dfJoined['target']==selected_class]
    filtered_df2 = df_norm[df_norm['target']==selected_class]

    traces2=[]
    #print(filtered_df.head())
    for axis in axes:
        [traces2.append(go.Scatter(
            x=filtered_df['shift'],
            y=filtered_df[axis],
            text=["shift, "+axis],
            mode='markers',
            opacity=0.7,
            marker=dict(size=10*(filtered_df2[axis])),
            name=axis
            ))]



    return {'data':traces2,
                'layout':go.Layout(title='Class-specific Comparison between Attributes (Bubble Chart)',
                                    xaxis={'title':'Shift'},
                                    yaxis={'title':'Sepal and Petal attributes'},
                                        hovermode='closest',
                                         paper_bgcolor='rgba(233,233,233,0)',
                                         plot_bgcolor='rgba(255,233,0,0)')}


# Callback for Tab 3 Graph 1
@app.callback(Output('graph3','figure'),
        [Input('row-picker','value')])
def update_figure(selected_row):
    """
    Function to update the graph based on selected row
    Arguments:
        selected_row: row selected as integer
    Returns:
        Updated Polar bar chart object

    """
    fig = create_polar(selected_row)
    return fig

# Callback for Tab 3 Graph 2
@app.callback(Output('graph4','figure'),
        [Input('row-picker','value')])
def update_figure(selected_row):

    """
    Function to update the graph based on selected row
    Arguments:
        selected_row: row selected as integer
    Returns:
        Updated guage object

    """
    fig = create_gauge(selected_row)
    return fig


# Callback for Tab 3 - Div tag to display class
@app.callback(
    Output(component_id='class_display', component_property='children'),
    [Input(component_id='row-picker', component_property='value')]
)
def update_output_div(input_value):
    """
    Function to update the graph based on selected row
    Arguments:
        selected_row: row selected as integer
    Returns:
        Updated Class value as string

    """
    row = input_value
    sample_df = df.iloc[row:row+1]
    target_class = sample_df['target'].values[0]

    return 'Class of selected record: "{}"'.format(target_options[target_class]['label'])



if __name__ == '__main__':
    #app.run_server(debug=True)

   app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)
