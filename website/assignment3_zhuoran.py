import dash
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
import numpy as np

from memoization import cached


@cached # Download data from yahoo finance
def download_data(ticker, period="max"):
    myTicker = yf.Ticker(ticker)
    hist = myTicker.history(period=period).reset_index()
    hist['Date'] = pd.to_datetime(hist['Date'], errors = 'coerce')
    return hist


@cached # Plot time series of the ticker
def plot_time_series(ticker, period="max"):
    ticker = ticker if ticker else "AAPL"
    hist = download_data(ticker, period)
    fig = px.scatter(hist, y="Open", x='Date')

    # The update_layout method allows us to give some formatting to the graph
    fig.update_layout(
        title_text = "Time Series Plot of {}".format(ticker) if period == "all" \
            else "Time Series Plot in a period of {} of {}".format(period, ticker),
        title_x = 0.5,
        yaxis = {
            'title': 'Price'}
    )
    
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
    return fig 


@cached
def calculate_volatility(ticker):
    hist = download_data(ticker)
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
    return data


@cached
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

@cached
def calculate_simulation(ticker,days=30, trials=100):
    hist = download_data(ticker)
    from scipy.stats import norm
    data=hist["Close"].pct_change()
    log_returns = np.log(1 + data)
    u = log_returns.mean()
    var = log_returns.var()
    drift = u - (0.5*var)
    stdev = log_returns.std()

    # Z = norm.ppf(np.random.rand(days, trials)) #days, trials
    Z = np.random.randn(days, trials)
    daily_returns = np.exp(drift + stdev * Z)
    price_paths = np.zeros_like(daily_returns)
    price_paths[0] = hist["Close"].iloc[-1]
    for t in range(1, days):
        price_paths[t] = price_paths[t-1]*daily_returns[t]

    price_paths=price_paths.T
    data2 = []
    last=[]
    for path in price_paths:
        last.append(path[-1])
        data2.append(
            go.Scatter
            (
            y = [i for i in path],
            x = [i for i in range(days)]
            )
        )
    
    return data2, last

@cached
def plot_simulation(input_value):
    data, last = calculate_simulation(input_value)
    fig = go.Figure(data = data)
    import plotly.express as px
    histog = px.histogram(last)
    fig.update_layout(
        title_text = "Monte Carlo simulation of {}".format(input_value),
        title_x = 0.5,
        yaxis = {
            'title': 'Price'}
    )
    histog.update_layout(
        title_text = "Distribution of prices in 30days of Monte Carlo simulation of {}".format(input_value),
        title_x = 0.5,
        yaxis = {
            'title': 'Price'}
    )
    return fig, histog


ticker = "AAPL"
hist = download_data(ticker)
fig_time_series = plot_time_series(ticker)
fig_time_series_period = plot_time_series(ticker, "1y")
fig_volatility = make_barchart(calculate_volatility(ticker))
figure_simulation, figure_simulation_histogram = plot_simulation(ticker)


#%% Dash app
app = Dash(
    prevent_initial_callbacks = True
)

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
        dcc.Graph(id='sim_plot', figure=figure_simulation),
        dcc.Graph(id='sim_hist', figure=figure_simulation_histogram),
        
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
        
        
        dcc.Graph(id='mul_plot', figure=fig_time_series_period),
        

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
        
        dcc.Graph(figure = fig_time_series, id="graphic"),

        html.Br(),
        dcc.Graph(figure = fig_volatility, id="bar")
        
        
    ],  #I could also put the list comprehension here
    style ={
        'margin': '2em',
        'border-radius': '1em',
        'border-style': 'solid', 
        'padding': '2em',
        'background': '#ededed'
    }
)

@app.callback(Output(component_id='sim_plot', component_property='figure'),
              Output(component_id='sim_hist', component_property='figure'),
                Input(component_id="my-input", component_property="value")
                )
def update_simulation(input_value="AAPL"):
    return plot_simulation(input_value)


@app.callback(Output(component_id='mul_plot', component_property='figure'),
                Input(component_id="my-input", component_property="value"),
                Input(component_id='dropdown', component_property='value')
                )
def update_time_series_period(input_value="AAPL",dropdown_value="max"):
    return plot_time_series(input_value,dropdown_value)


@app.callback(
    Output(component_id="graphic", component_property="figure"),
    Output(component_id="bar", component_property="figure"),
    Input(component_id="my-input", component_property="value")
)
def update_time_series(ticker="AAPL"):
    fig_time_series = plot_time_series(ticker)
    fig_volatility = make_barchart(calculate_volatility(ticker))
    return fig_time_series, fig_volatility


if __name__ == "__main__":
    print('About to start...')
                    
    app.run_server(
        debug = True,
        port = 8062
    )

# simulation(ticker="AAPL",days=30, trials=100)
