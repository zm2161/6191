
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

    # hist['Date'].max()

ticker = "AAPL"
hist = download_data(ticker)

from scipy.stats import norm
data=hist["Close"].pct_change()
log_returns = np.log(1 + data)
u = log_returns.mean()
var = log_returns.var()
drift = u - (0.5*var)
stdev = log_returns.std()
days = 30
trials = 10000
Z = norm.ppf(np.random.rand(days, trials)) #days, trials
daily_returns = np.exp(drift.values + stdev.values * Z)
price_paths = np.zeros_like(daily_returns)
price_paths[0] = data.iloc[-1]
for t in range(1, days):
    price_paths[t] = price_paths[t-1]*daily_returns[t]


#%% Graph generation
fig = px.scatter(hist, y="Open", x='Date')

# The update_layout method allows us to give some formatting to the graph
fig.update_layout(
    title_text = "Time Series Plot of {}".format(ticker),
    title_x = 0.5,
    yaxis = {
        'title': 'Price'}
)


# here another blank no change4

# Add range slider
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
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
            visible=False
        ),
        # type="date",
        # title='This is a date'
    )
)

# 
hist["returns"] = hist["Close"].pct_change()
hist.dropna(inplace=True)

hist["labels"] = pd.qcut(hist["Volume"], 20)
returns_mean = hist.groupby("labels")["returns"].mean()

data = []
data.append(
    go.Bar(
    name = "returns distribution",
    x = [f"{round(x.left, -len(str(x.left))+4)}-{round(x.right, -len(str(x.right))+4)}" for x in returns_mean.index.categories],
    y = returns_mean.tolist()
    )
)


def make_barchart(data):
    fig = go.Figure(data = data)

    fig.update_layout(
        barmode = 'group',
        title = 'Bar Chart of Equity Returns grouped by Volume',
        paper_bgcolor = 'white',
        plot_bgcolor = 'white',
        xaxis = dict(
            showline = True, 
            linewidth = 2, 
            linecolor = 'black'
        ),
        yaxis=dict(
            title = 'Stock Returns',
            titlefont_size = 16,
            tickfont_size = 14,
            gridcolor = '#dfe5ed'
        )
    )

    fig.layout.hovermode = 'x'
    return(fig)

fig2 = make_barchart(data)

def download_data_time(ticker, period_new):
    myTicker = yf.Ticker(ticker)
    hist = myTicker.history(period=period_new)

    hist = hist.reset_index()
    hist['Date'] = pd.to_datetime(hist['Date'], errors = 'coerce')
    return hist

    # hist['Date'].max()


#%% Dash app
app = Dash()

app.layout = html.Div(
    [
        "See how it will be displayed",
        html.Center(html.H4('My Second Dash App - Yey!!!')),
        html.Br(),
        html.Br(),

        dcc.Input(
            id="my-input",
            type="text",
            placeholder="Please input stock symbol name Default AAPL: ",
            style={ "width": "20%"}
        ),

        html.Br(),
        html.Br(),
        dcc.Dropdown(id='dropdown',
        options=[{'label': 'max', 'value': 'max'},
                {'label': '1y', 'value': '1y'},
                {'label': '6mo', 'value': '6mo'},
                {'label': '1mo', 'value': '1mo'},
                {'label': '5d', 'value': '5d'}],
            placeholder = 'max'
            #options=[{'labels': comp['label'], 'value':comp['label']} for comp in comp_options]
        ),
        #html.H4('Price graph of different period', style = {'text-align': 'center', 'color':'blue','font-weight': 'bold'}),
        # multiple line of text
        
        
        dcc.Graph(id='mul_plot'),
        

        html.Br(),
        html.Div(id='my-output'),

        # dcc.Dropdown(
        #     options=[
        #         dict(label="GOOG", value=0),
        #         dict(label="AAPL", value=1),
        #         dict(label="SPX", value=2),
        #     ],
        #     placeholder = "Select symbol"
        # ),



        html.Div('''
             This app displays a graph of the entire price history of {}.'''.format(ticker),
             style = {
                 'width': '60%',
                 'text-align': 'center',
                 'margin-left': 'auto',
                 'margin-right': 'auto',
             }
        ),
        
        dcc.Graph(figure = fig, id="graphic"),

        html.Br(),
        dcc.Graph(figure = fig2, id="bar")
        
        
    ],  #I could also put the list comprehension here
    style ={
        'margin': '2em',
        'border-radius': '1em',
        'border-style': 'solid', 
        'padding': '2em',
        'background': '#ededed'
    }
)
@app.callback(Output(component_id='mul_plot', component_property='figure'),
                Input(component_id="my-input", component_property="value"),
                Input(component_id='dropdown', component_property='value')
                )
def graph_update(input_value,dropdown_value):
    print(dropdown_value)
    ticker = input_value if input_value else "AAPL"
    hist = download_data_time(ticker,dropdown_value)
    fig = px.scatter(hist, y="Open", x='Date')

    # The update_layout method allows us to give some formatting to the graph
    fig.update_layout(
        title_text = "Time Series Plot in a period of {} of {}".format(dropdown_value, input_value),
        title_x = 0.5,
        yaxis = {
            'title': 'Price'}
    )
    
    return fig 

@app.callback(
    Output(component_id="graphic", component_property="figure"),
    Output(component_id="bar", component_property="figure"),
    Input(component_id="my-input", component_property="value")
)
def update_output_div(input_value):
    # return f'Output: {input_value}'
    ticker = input_value if input_value else "AAPL"
    hist = download_data(ticker)
    #%% Graph generation
    fig = px.scatter(hist, y="Open", x='Date')

    # The update_layout method allows us to give some formatting to the graph
    fig.update_layout(
        title_text = "Time Series Plot of {}".format(ticker),
        title_x = 0.5,
        yaxis = {
            'title': 'Price'}
    )

    hist["returns"] = hist["Close"].pct_change()
    hist.dropna(inplace=True)

    hist["labels"] = pd.qcut(hist["Volume"], 20)
    returns_mean = hist.groupby("labels")["returns"].mean()

    data = []
    data.append(
        go.Bar(
        name = "returns distribution",
        x = [f"{round(x.left, -len(str(x.left))+4)}-{round(x.right, -len(str(x.right))+4)}" for x in returns_mean.index.categories],
        y = returns_mean.tolist()
        )
    )
    fig2 = make_barchart(data)
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
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
            title='This is a date'
        )
    )
    return fig, fig2



print('About to start...')
                
app.run_server(
    debug = True,
    port = 8061
)


_# %%
