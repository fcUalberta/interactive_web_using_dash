# Importing libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from plotly.subplots import make_subplots
import dash_table

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

target_options = []

# Storing the class names based on class numbers 0 or 1
for cls in range(0,2):
    if cls == 0:
        target_options.append({'label':'Class Not Versicolor','value':cls})
    else:
        target_options.append({'label':'Class Versicolor','value':cls})


def create_polar(row):
    """
    Function to create the polar-bar chart_box

    Arguments:
        row: Selected row
    Returns:
        Figure object
    """
    #row=0
    fig = make_subplots(rows=1,cols=2,shared_yaxes= True,
                        specs=[[{'type': 'polar'}]*2],
                        subplot_titles=("Selected Record","Represented Class"))

    sample_df1 = df.iloc[row:row+1]
    sample_df2 = df_norm.iloc[row:row+1]
    target_class = sample_df1['target'].values[0]
    #print(target_class,target_options[target_class]['label'])
    filtered_df = df[df['target']==target_class]
    filtered_df2 = df_norm[df_norm['target']==target_class]
    category_avg = filtered_df2.mean(axis=0).tolist()
    category_avg = [ round(elem, 2) for elem in category_avg ]

    print(filtered_df)
    print(category_avg)
    [fig.add_trace(go.Barpolar(
                    r=list(sample_df2.loc[:,'sepal length':'petal width'].values)[0],
                    theta=[45,135,225,270],
                    #width=[15,15,15,15],
                    marker_color=["#E4FF87", '#70DDFF', '#709BFF', '#FFAA70'],
                    marker_line_color="black",
                    marker_line_width=2,
                    text = list(sample_df2.loc[:,'sepal length':'petal width'].columns),
                    hoverinfo = "text",
                    opacity=0.8
        ),row=1,col=1)]

    [fig.add_trace(go.Barpolar(

                    r=category_avg[0:4],
                    theta=[45,135,225,270],
                    #width=[15,15,15,15],
                    marker_color=["#E4FF87", '#70DDFF', '#709BFF', '#FFAA70'],
                    marker_line_color="black",
                    marker_line_width=2,
                    text = list(sample_df2.loc[:,'sepal length':'petal width'].columns),
                    hoverinfo = "text",
                    #hovertext = "text",
                    opacity=0.8
        ),row=1,col=2)]
    title = "Comparison of Record \""+str(row)+"\" Vs \"" + target_options[target_class]['label']+ "\" Average"
    fig.update_layout(title=title,
    template=None,
    paper_bgcolor='rgba(233,233,233,0)',
    plot_bgcolor='rgba(255,233,0,0)',
    height = 500,

    polar = dict(
    radialaxis = dict(range=[0, 7], showticklabels=False, ticks=''),
    angularaxis = dict(showticklabels=True, ticks=''),
    angularaxis_categoryarray = ["d", "a", "c", "b"]),

    polar2 = dict(
    radialaxis = dict(range=[0, 7], showticklabels=False, ticks=''),
    angularaxis = dict(showticklabels=True, ticks='')),
    showlegend=False
    )


    return fig

# fig2 = create_polar(0)

def create_pairwise():
    """
    Function to create the Pair-wise Scatter matrix

    Arguments:None
    Returns:
        Figure object
    """

    fig = go.Figure(data=go.Splom(
                dimensions=[dict(label=axes[0],
                                 values=df[axes[0]]),
                            dict(label=axes[1],
                                values=df[axes[1]]),
                            dict(label=axes[2],
                                values=df[axes[2]]),
                            dict(label=axes[3],
                                values=df[axes[3]])],
                showupperhalf=False,
                #diagonal_visible=False,# remove plots on diagonal
                text=axes,
                marker=dict(
                            color=df["target"],
                            showscale=True,
                            #showlegend=True,
                            #colorscale = 'Bluered',
                            line_color='grey', line_width=0.5)
                ))

    fig.update_layout(
        #title='Pair-wise Comparison of Attributes ',
        width=700,
        height=600,
        paper_bgcolor='rgba(233,233,233,0)',
        plot_bgcolor='rgba(255,233,0,0)',
        )
    return fig

# fig5 = create_pairwise()

def create_gauge(row):

    """
    Function to create the 8 Gauge chart subplots

    Arguments:
        row: Selected row
    Returns:
        Figure object
    """

    fig = make_subplots(rows=2,cols=4,
                            specs=[[{"type": "indicator"}, {"type": "indicator"},{"type": "indicator"}, {"type": "indicator"}],
                                [{"type": "indicator"}, {"type": "indicator"},{"type": "indicator"}, {"type": "indicator"}]],
                            subplot_titles=[axes[0]+"-record",axes[1]+"-record",axes[2]+"-record",axes[3]+"-record",
                                            axes[0]+"-class",axes[1]+"-class",axes[2]+"-class",axes[3]+"-class"]
                         )

    sample_df1 = df.iloc[row:row+1]
    sample_df2 = df_norm.iloc[row:row+1]
    target_class = sample_df1['target'].values[0]
    filtered_df = df[df['target']==target_class]
    filtered_df2 = df_norm[df_norm['target']==target_class]
    category_avg = filtered_df.mean(axis=0).tolist()
    category_avg = [ round(elem, 2) for elem in category_avg ]

    c = [1,2,3,4]
    colors = ["#E4FF87", '#70DDFF', '#709BFF', '#FFAA70']
    for i,axis in zip(c,axes):
        [fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = float(sample_df1[axis]) ,
            domain = {'x': [0,1], 'y': [0,1]},
            delta = {'reference': float(category_avg[i-1]), 'increasing': {'color': "RebeccaPurple"}},
            gauge = {'bar':{'color':colors[i-1]},
                    'axis': {'range': [-4, 4]}}
                    # 'steps': [
                    #     {'range': [-4, 0], 'color': 'white'},
                    #     {'range': [0.1, 4], 'color': 'red'}]}
            #title = {'text': axis})
            ),row=1,col=i)]
    for i,axis in zip(c,axes):
        [fig.add_trace(go.Indicator(
        mode = "gauge+number",
        value = float(category_avg[i-1]) ,
        domain = {'x': [0,1], 'y': [0,1]},
            gauge = {'bar':{'color':colors[i-1]},
                    'axis': {'range': [-4, 4]}},
        delta = {'reference': 0, 'increasing': {'color': "RebeccaPurple"}},
        #title = {'text': axis})
        ),row=2,col=i)]

    fig.update_layout(paper_bgcolor='rgba(233,233,233,0)',
    plot_bgcolor='rgba(255,233,0,0)')
    for i in range(0,8):
        fig.layout.annotations[i]["font"] = {'size': 12}

    return fig

    # fig4 = create_gauge(0)
# def create_table(row):
#     initial_table = df_table.iloc[row:row+1]
#     target_class = initial_table['target'].values[0]
#     df_category=df_table[df_table['target']==target_class]
#     df_category_avg = pd.DataFrame(df_category.mean(axis=0)).T.round(decimals=2)
#     return initial_table,df_category,df_category_avg
#
# #print(target_options)
# initial_table,df_category,df_category_avg=create_table(0)
