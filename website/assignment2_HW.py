
import dash
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
import numpy as np

#%% Data Download Section


def download_data(ticker):
    myTicker = yf.Ticker(ticker)
    hist = myTicker.history(period="max")
    hist = hist.reset_index()
    hist['Date'] = pd.to_datetime(hist['Date'], errors = 'coerce')
    return hist


def download_data_list(ticker_list):
    ticker_string = ', '.join(ticker_list)
    myTicker = yf.Tickers(ticker_string)
    hist = myTicker.history(period="max")
    return hist


ticker_list = ["AAPL", "MSFT"]
hist_list = download_data_list(ticker_list)
fig1 = go.Figure()
df_new = hist_list['Close'][['AAPL']].dropna()
fig1.add_trace(go.Scatter(y=df_new['AAPL'].to_list(), x=df_new.index.to_list()))
df_new = hist_list['Close'][['MSFT']].dropna()
fig1.add_trace(go.Scatter(y=df_new['MSFT'].to_list(), x=df_new.index.to_list()))
names_list = ticker_list.copy()
fig1.for_each_trace(lambda t: t.update(name=names_list.pop(0)))

# I can call the update method enbedded in plotly express:
fig1.update_layout(
    # this is a function taking multiple kwargs where complex args have to be passed as dictionaries
    title = {
        'text': 'American Airlines Historical Price',
        'y': 0.95,
        'x': 0.5,
        'font': {'size': 22}
    },
    paper_bgcolor = 'white',
    plot_bgcolor = 'white',
    autosize = False,
    height = 400,
    xaxis = {
        'title': 'Closing Date',
        'showline': True,
        'linewidth': 1,
        'linecolor': 'black'
    },
    yaxis = {
        'showline': True,
        'linewidth': 1,
        'linecolor': 'black'
    }
)

# This updates the data portion
fig1.update_layout(
    xaxis=dict(
        rangeselector = dict(
            buttons = list([
                dict(count=1,
                     label="1m",
                     step="month",
                     # stepmode="backward"
                     ),
                dict(count=6,
                     label="6m",
                     step="month",
                     # stepmode="backward"
                     ),
                dict(count=1,
                     label="YTD",
                     step="year",
                     # stepmode="todate"
                     ),
                dict(count=1,
                     label="1y",
                     step="year",
                     # stepmode="backward"
                     ),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date",
    )
)


#%% Dash app
app = Dash()

app.layout = html.Div(
    [
        "See how it will be displayed",
        html.Center(html.H4('My Third Dash App - Woohoo!')),
        html.Br(),
        dcc.Input(
            id="my-input",
            type="text",
            placeholder="Please input stock symbol name Default AAPL: ",
            style={ "width": "20%"}
        ),

        html.Br(),
        html.Div(id='my-output'),

        html.Div('''
             This app displays a graph of the entire price history of AAPL.''',
             style = {
                 'width': '60%',
                 'text-align': 'center',
                 'margin-left': 'auto',
                 'margin-right': 'auto',
             }
        ),
        
        dcc.Graph(figure=fig1, id="graphic"),

    ],  # I could also put the list comprehension here
    style=
    {
        'margin': '2em',
        'border-radius': '1em',
        'border-style': 'solid', 
        'padding': '2em',
        'background': '#ededed'
    }
)


@app.callback(
    Output(component_id="graphic", component_property="figure"),
    Input(component_id="my-input", component_property="value")
)
def update_output_div(input_value):
    # return f'Output: {input_value}
    if input_value and len(input_value) == 4 and input_value not in ticker_list:
        ticker_list.append(input_value)
        print(ticker_list)
        hist_list = download_data_list(ticker_list)
        # Graph generation
        df_new = hist_list["Close"][[ticker_list[-1]]].dropna()
        fig1.add_trace(go.Scatter(y=df_new[ticker_list[-1]].to_list(), x=df_new.index.to_list()))
        names_list = ticker_list.copy()
        fig1.for_each_trace(lambda t: t.update(name=names_list.pop(0)))

    return fig1


print('About to start...')
                
app.run_server(
    debug=True,
    port=8061
)


# %%
