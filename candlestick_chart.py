#!/bin/env -S python3
"""
Python functions to create various stock analaysis charts.
"""

# Import packages
import os
import logging
from datetime import datetime
import pandas
import numpy
import yfinance
from matplotlib import pyplot
from mplfinance.original_flavor import candlestick_ohlc

# Function to create a candlestick_ohlc base chart using mplfinance.
def graph_candlestick(dataframe, **kwargs):
    """
    Graphs a candlestick_ohlc chart using mplfinance.
    """

    # keywords & vars
    symbol = kwargs.get('symbol', '')
    interval = kwargs.get('interval', 'NaN')
    period = kwargs.get('period', 'NaN')

    name = yfinance.Ticker(symbol).info['shortName']

    xdate = [datetime.strptime(x[:-6],
        '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d\n%A') for x in dataframe.Datetime]

    pyplot.figure(figsize=(12,3), dpi=80)
    pyplot.style.use('bmh')
    pyplot.title(f'{symbol} - {name}', loc='left')

    pyplot.xticks(numpy.arange(0, len(dataframe), step=28), xdate[::28], fontsize=8, rotation=45)

    #pyplot.xlabel('Date', fontsize=6)
    #pyplot.ylabel('Price', fontsize=6, color='grey')

    ax1 = pyplot.subplot(1,1,1)
    ax1.yaxis.tick_right()

    #Create a new DataFrame which includes OHLC data for each period specified by stick input
    plotdata = pandas.DataFrame(
        {
            "Open":dataframe["Open"],
            "High":dataframe["High"],
            "Low":dataframe["Low"],
            "Close":dataframe["Close"]
        }
    )

    # Create the candelstick chart
    candlestick_ohlc(ax1, list(zip(list(plotdata.index.tolist()),
            plotdata["Open"].tolist(),
            plotdata["High"].tolist(),
            plotdata["Low"].tolist(),
            plotdata["Close"].tolist()
        )),
        width = 0.55,
        colorup = "green",
        colordown = "red"
    )

    ax1.text(0.01, 0.04, f'interval: {interval}\nperiod: {period}',
        transform=ax1.transAxes, fontsize=6, color='gray', alpha=0.5,
        ha='left', va='bottom')

    return pyplot

# Function to create a Bollinger Bands overlay chart
def overlay_bollinger(dataframe, **kwargs):
    """
    A Bollinger Band is a set of trendlines plotted two standard deviations
    (positively and negatively) away from a simple moving average (SMA) of a
    security's price.
    """

    # keywords & vars
    num_of_std  = kwargs.get('num_of_std', 2)
    window_size = kwargs.get('window_size', 20)

    # plot chart type in title
    pyplot.title('Bollinger Bands', loc='right', fontsize=6, color='darkblue')

    # create rolling mean and standard deviation
    rolling_mean = dataframe['Close'].rolling(window=window_size).mean()
    rolling_std = dataframe['Close'].rolling(window=window_size).std()

    # create upper and lower bands
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)

    # plot stock data, rolling mean and Bollinger Bands
    pyplot.plot(rolling_mean, label='Rolling Mean', linewidth=0.5, linestyle='dashed', color='gray')
    pyplot.plot(upper_band, label='Upper band', linewidth=0.5, color='blue')
    pyplot.plot(lower_band, label='Lower band', linewidth=0.5, color='purple')

    pyplot.fill_between(dataframe.index,
        upper_band, lower_band,
        where=upper_band > lower_band,
        color='lightgrey', alpha=0.2)

    # Show legend on the plot
    pyplot.legend(loc='upper left', fontsize=6)

    return pyplot

# Function to create an Ichimoku overlay chart.
def overlay_ichimoku(dataframe, **kwargs):
    """
    The Ichimoku chart shows support and resistance levels, as well as other essential
    information such as trend direction and momentum. Compared to standard candlestick
    charts, the Ichimoku Cloud contains more data points, increasing the accuracy of
    forecast price moves.
    """

    # Keywords & vars
    tenkan   = kwargs.get('tenkan', 9)
    kijun    = kwargs.get('kijun', 26)
    senkou_b = kwargs.get('senkou_b', 52)

    # Plot chart type in title
    pyplot.title('Ichimoku Kinko Hyo', loc='right', fontsize=6, color='darkblue')

    # Append null row at the end of the dataframe
    dataframe = pandas.concat([dataframe, pandas.DataFrame(numpy.zeros((senkou_b,
        len(dataframe.columns))))]).reset_index(drop=True)

    # Calculate ichimoku data
    dataframe['Tenkan_sen']  = (dataframe['High'].rolling(tenkan).max() + \
            dataframe['Low'].rolling(tenkan).min()) / 2
    dataframe['Kijun_sen']   = (dataframe['High'].rolling(kijun).max() + \
            dataframe['Low'].rolling(kijun).min()) / 2
    dataframe['Senkou_a']    = ((dataframe['Tenkan_sen'] + \
            dataframe['Kijun_sen']) / 2).shift(senkou_b)
    dataframe['Senkou_b']    = ((dataframe['High'].rolling(senkou_b).max() + \
            dataframe['Low'].rolling(senkou_b).min()) / 2).shift(senkou_b)
    dataframe['Chikou_span'] = dataframe['Close'].shift(-26)

    # Plot the Ichimoku chart
    pyplot.plot(dataframe['Tenkan_sen'], label='Tenkan-sen',
            linewidth=0.4, color='darkorange')
    pyplot.plot(dataframe['Kijun_sen'], label='Kijun-Sen',
            linewidth=0.4, color='purple')
    pyplot.plot(dataframe['Senkou_a'], label='Senkou Span A',
            linewidth=0.4, alpha=0.05, color='grey')
    pyplot.plot(dataframe['Senkou_b'], label='Senkou Span B',
            linewidth=0.6, color='red')
    pyplot.plot(dataframe['Chikou_span'], label='Chikou Span',
            linewidth=1, linestyle='dashed', alpha=0.5, color='cyan')

    # Plot Kumo (Cloud)
    pyplot.fill_between(dataframe.index,
        dataframe['Senkou_a'], dataframe['Senkou_b'],
        where=dataframe['Senkou_a'] >= dataframe['Senkou_b'],
        color='grey', alpha=0.2)
    pyplot.fill_between(dataframe.index,
        dataframe['Senkou_a'], dataframe['Senkou_b'],
        where=dataframe['Senkou_a'] < dataframe['Senkou_b'],
        color='orange', alpha=0.2)

    # Show legend on the plot
    pyplot.legend(loc='upper left', fontsize=6)

    return pyplot

# Function to create a VWAP overlay chart.
def overlay_vwap(dataframe):
    """
    VWAP represents the average price a security has traded at throughout the day,
    based on both volume and price.
    """

    # plot chart type in title
    pyplot.title('Volume-Weighted Average Price', loc='right', fontsize=6, color='darkblue')

    # create VWAP column
    dataframe['VWAP'] = (dataframe['Close'] * dataframe['Volume']).cumsum() \
                            / dataframe['Volume'].cumsum()

    # plot VWAP data
    pyplot.plot(dataframe['VWAP'], label='VWAP', linewidth=0.8, color='blue')

    # Show legend on the plot
    pyplot.legend(loc='upper left', fontsize=6)

    return pyplot

if __name__ == "__main__":
    # Set environment basename for output files
    basename = os.path.splitext(os.path.basename(__file__))[0]

    # Initialize logging
    logfile = os.path.expanduser(f'~/public_html/{basename}.log')
    logging.basicConfig(level=logging.DEBUG, encoding="utf-8",
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=logfile)

    # Test Constant Variables
    SYMBOL   = "SNAP"
    INTERVAL = "15m"
    PERIOD   = "14d"

    # Read historical data from Yahoo Finance
    csvfile = os.path.expanduser(f'~/public_html/{basename}.csv')
    if not os.path.exists(csvfile):
        df = yfinance.download(SYMBOL, interval=INTERVAL, period=PERIOD)
        df.to_csv(csvfile)

    # Read the data from the CSV file
    df = pandas.read_csv(csvfile)

    # Plot the data
    graph = graph_candlestick(df, symbol=SYMBOL, interval=INTERVAL, period=PERIOD)
    #grahp = overlay_vwap(df)
    #graph = overlay_bollinger(df)
    graph = overlay_ichimoku(df)

    # Save the plot to a PNG file
    pngfile = os.path.expanduser(f'~/public_html/{basename}.png')
    graph.savefig(pngfile, dpi=600, bbox_inches='tight', pad_inches=0.1)
    graph.close()
