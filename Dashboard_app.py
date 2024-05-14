#!/usr/bin/env python
# coding: utf-8

# In[18]:


import pandas as pd
from pylab import rcParams
import matplotlib.pyplot as plt
import dash_auth

import plotly
import plotly.graph_objects as go
from datetime import datetime

import dash
import dash_core_components as dcc 
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output


ALL_DATA=pd.read_csv('Datos/PROYECCIONES.csv', encoding='latin-1')
BASE=pd.read_csv('Datos/BASE.csv', encoding='latin-1')


ALL_DATA=ALL_DATA[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'RECURSO']]
BASE=BASE[['ds', 'y','RECURSO']]


ANTES=pd.read_csv('Datos/ANTES.csv', encoding='latin-1')
DESPUES=pd.read_csv('Datos/DESPUES.csv', encoding='latin-1')

ANTES['CLUSTER']='BASE'
DESPUES['CLUSTER']='SE AGRUPARON'



BASE['PERIODO']=BASE['ds'].str.split('-', expand=True)[0]
ALL_DATA['PERIODO']=ALL_DATA['ds'].str.split('-', expand=True)[0]


INFO_GENERAL=pd.read_csv('Datos/GENERAL.csv', encoding='latin-1')


#VALID_USERNAME_PASSWORD_PAIRS = {
 #   'OGUTI': 'OGUTI','HERDEZ': 'HERDEZ'
#}
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
#auth = dash_auth.BasicAuth(app,VALID_USERNAME_PASSWORD_PAIRS)
app.layout = html.Div([
    
    html.Div([
        html.H1('Test de Cluster, Forecast y Características ', style={'fontSize': 30,'font-family':'sans-serif', 'color':'red'}),
        html.Img(src='assets/enigma.png')
    ],style = {}, className = 'banner'),

    html.Div([
        html.Div([
            html.P('Da click en la barra y selecciona el RECURSO/CLUSTER :', className = 'fix_label', style={'fontSize': 20,'color':'green', 'margin-top': '4px'}),
            dcc.Dropdown(id="RECURSO",options=ALL_DATA['RECURSO'].unique().tolist(),value='8',multi=False,className="dropdown"
        )]),
    ]),
    html.Div([
        html.Div([
            html.P('Da click en el número de semanas de proyección :', className = 'fix_label', style={'fontSize': 18,'color':'green', 'margin-top': '4px'}),
             dcc.Slider(min=1, max=20, step=1,value=12,id='COBERTURA')]),
    ]),

##################################################################------------------------------
    html.Div([
        html.Div([
            dcc.Graph(id = 'CURVAS', figure = {})
        ], className = 'create_container1 eight columns'),
        html.Div([
            dcc.Graph(id = 'INDICADOR', figure = {})
        ], className = 'create_container1 four columns'),
        html.Div([
            dcc.Graph(id = 'INDICADORR', figure = {})
        ], className = 'create_container1 four columns'),
        
    ], className = 'row flex-display'),
    
##################################################################------------------------------
    html.Div([
        html.H1('"RECURSO" asignado por Clusterizacion', style={'fontSize': 25,'font-family':'sans-serif'})
    ],style = {}, className = 'banner3'),
    
    html.Div([
        html.Div([
            dcc.Graph(id = 'INDICADOR6', figure = {})
        ], className = 'create_container1 five columns'),
        html.Div([
            dcc.Graph(id = 'INDICADOR5', figure = {})
        ], className = 'create_container1 eight columns'),
        
    ], className = 'row flex-display'),
    
##################################################################------------------------------
    html.Div([
        html.H1('Composición del volumen de venta', style={'fontSize': 25,'font-family':'sans-serif'})
    ],style = {}, className = 'banner3'),
    
    html.Div([
        html.Div([
            dcc.Graph(id = 'INDICADOR2', figure = {})
        ], className = 'create_container1 five columns'),
        html.Div([
            dcc.Graph(id = 'INDICADOR3', figure = {})
        ], className = 'create_container1 five columns'),
        html.Div([
            dcc.Graph(id = 'INDICADOR4', figure = {})
        ], className = 'create_container1 five columns'),
        
    ], className = 'row flex-display'),
    
##################################################################------------------------------
    html.Div([
        html.H1('', style={'fontSize': 25,'font-family':'sans-serif'})
    ],style = {}, className = 'banner2'),
##################################################################------------------------------
], id='mainContainer', style={'display':'flex', 'flex-direction':'column'})


@app.callback(
    Output("CURVAS", "figure"),
    [Input("RECURSO","value")
    ])
def update_graph(recurso):
    df_forecast=ALL_DATA[ALL_DATA['RECURSO']==recurso]
    base=BASE[BASE['RECURSO']==recurso]

    trace_open = go.Scatter(x = df_forecast["ds"],y = df_forecast["yhat"],mode = 'lines',name="Modelo predictivo")
    trace_high = go.Scatter(x = df_forecast["ds"],y = df_forecast["yhat_upper"],mode = 'lines',fill = "tonexty", line = {"color": "#57b8ff"}, name="Margen superior")
    trace_low = go.Scatter(x = df_forecast["ds"],y = df_forecast["yhat_lower"],mode = 'lines',fill = "tonexty", line = {"color": "#57b8ff"}, name="Margen inferior")
    trace_close = go.Scatter(x = base["ds"],y = base["y"],name="Datos")

    data = [trace_open,trace_high,trace_low,trace_close]
    layout = go.Layout(title="Modelo para la prediccion de volumen para 20 semanas",xaxis_rangeslider_visible=True)

    fig = go.Figure(data=data,layout=layout)
    fig.update_layout(height=400)
    return fig

@app.callback(
    Output("INDICADOR", "figure"),
    [Input("RECURSO","value"),
     Input("COBERTURA","value")
    ])
def update_graph(recurso,cobertura):
    num=ALL_DATA[(ALL_DATA['PERIODO']=='2023')&(ALL_DATA['RECURSO']==recurso)].head(cobertura)[['yhat']].sum()
    num=int(num)
    if num < 0:
        num=0
    fig = go.Figure()
    fig.add_trace(go.Indicator(mode = "number",value = num,domain = {'row': 0, 'column': 1}))

    fig.update_layout(grid = {'rows': 1, 'columns': 1, 'pattern': "independent"},
        template = {'data' : {'indicator': [{'title': {'text': "Proyección de volumen de venta"}}]}})
    fig.update_layout(title='Proyeccion de volumen desplazado - '+str(cobertura)+' Semanas',height=400)
    return fig

@app.callback(
    Output("INDICADORR", "figure"),
    [Input("RECURSO","value"),
     Input("COBERTURA","value")
    ])
def update_graph(recurso,cobertura):
    anterior_menos1=BASE[(BASE['PERIODO']=='2021')&(BASE['RECURSO']==recurso)].head(cobertura)[['y']].sum()
    anterior=BASE[(BASE['PERIODO']=='2022')&(BASE['RECURSO']==recurso)].head(cobertura)[['y']].sum()
    proyeccion=ALL_DATA[(ALL_DATA['PERIODO']=='2023')&(ALL_DATA['RECURSO']==recurso)].head(cobertura)[['yhat']].sum()
    
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = int(anterior_menos1),
        title = {"text": "Anterior vs Proyección<br>"},
        delta = {'reference': int(proyeccion) , 'relative': True,"valueformat": ".2f"},
        domain = {'x': [0.4, .7], 'y': [.57, .99]}))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = int(anterior),
        title = {"text": "Anterior_menos1 vs Proyección<br>"},
        delta = {'reference': int(proyeccion), 'relative': True,"valueformat": ".2f"},
        domain = {'x': [0.4,.7], 'y': [.01, .50]}))
    fig.update_layout(title='Volumen en periodos anteriores - '+str(cobertura)+' Semanas',height=400)
    return fig

@app.callback(
    Output("INDICADOR2", "figure"),
    [Input("RECURSO","value"),
    ])
def update_graph(recurso):
    DATOSS=INFO_GENERAL[(INFO_GENERAL['RECURSO']==recurso)&(INFO_GENERAL['UNIDADES_EN_000']>0)]
    fig = px.sunburst(DATOSS, path=['TIPO', 'SUBTIPO'], values='UNIDADES_EN_000',
                      color='UNIDADES_EN_000',
                      color_continuous_scale='RdBu')
    fig.update_layout(title='COMPOSICIÓN DE VENTA, TIPO y SUBTIPO',height=450)
    return fig

@app.callback(
    Output("INDICADOR3", "figure"),
    [Input("RECURSO","value"),
    ])
def update_graph(recurso):
    DATOSS=INFO_GENERAL[(INFO_GENERAL['RECURSO']==recurso)&(INFO_GENERAL['UNIDADES_EN_000']>0)]
    fig = px.sunburst(DATOSS, path=['SEGMENTO', 'SUBSEGMENTO'], values='UNIDADES_EN_000',
                      color='UNIDADES_EN_000',
                      color_continuous_scale='RdBu')
    fig.update_layout(title='COMPOSICIÓN DE VENTA, SEGMENTO Y SUBSEGMENTO',height=450)

    return fig

@app.callback(
    Output("INDICADOR4", "figure"),
    [Input("RECURSO","value"),
    ])
def update_graph(recurso):
    DATOSS=INFO_GENERAL[(INFO_GENERAL['RECURSO']==recurso)&(INFO_GENERAL['UNIDADES_EN_000']>0)]
    fig = px.sunburst(DATOSS, path=['INGREDIENTES', 'SABOR'], values='UNIDADES_EN_000',color='UNIDADES_EN_000',
                      color_continuous_scale='RdBu')
    fig.update_layout(title='COMPOSICIÓN DE VENTA, INGREDIENTES Y SABOR',height=450)

    return fig

@app.callback(
    Output("INDICADOR5", "figure"),
    [Input("RECURSO","value"),
    ])
def update_graph(recurso):
    ALL=pd.concat([ANTES[ANTES['RECURSO']==recurso],DESPUES[DESPUES['RECURSO']==recurso]])
    fig = px.scatter(ALL, x="VALOR_EN_000_PESOS", y="UNIDADES_EN_000", color="CLUSTER", symbol="CLUSTER")
    fig.update_layout(title='GAFICA QUE MUESTRA ELEMENTOS AGRUPADOS POR CLUSTER',height=400)

    return fig

@app.callback(
    Output("INDICADOR6", "figure"),
    [Input("RECURSO","value"),
    ])
def update_graph(recurso):
    num=len(DESPUES[DESPUES['RECURSO']==recurso])
    num=int(num)
    fig = go.Figure()
    fig.add_trace(go.Indicator(mode = "number",value = num,domain = {'row': 0, 'column': 1}))

    fig.update_layout(grid = {'rows': 1, 'columns': 1, 'pattern': "independent"},
        template = {'data' : {'indicator': [{'title': {'text': "Registros agregados"}}]}})
    fig.update_layout(title='Registros aregados por clustering',height=400)
    return fig


if __name__ == ('__main__'):
    app.run_server()


