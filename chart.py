#!/bin/env -S python3
"""
chart.py - A module to create various stock analaysis charts.
"""

# Import packages
import os, logging
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mplfinance.original_flavor import candlestick_ohlc
import numpy as np
import yfinance as yf

# Function to create a candlestick_ohlc base chart using mplfinance.
def graph_candlestick(dataframe, *args, **kwargs):
    """
    Graphs a candlestick_ohlc chart using mplfinance.
    """

    # keywords & vars
    ticker = kwargs.get('ticker', '')
    interval = kwargs.get('interval', 'NaN')
    period = kwargs.get('period', 'NaN')
    xdate = [dt.datetime.strptime(x[:-6], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d\n%A') for x in dataframe.Datetime]

    plt.figure(figsize=(12,3))
    plt.style.use('bmh')
    plt.title('{}'.format(ticker), loc='left')

    plt.xticks(np.arange(0, len(dataframe), step=28), xdate[::28], fontsize=8, rotation=45)

    #plt.xlabel('Date', fontsize=6)
    #plt.ylabel('Price', fontsize=6, color='grey')

    ax1 = plt.subplot(1,1,1)

    #Create a new DataFrame which includes OHLC data for each period specified by stick input
    plotdata = pd.DataFrame(
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

    ax1.text(0.01, 0.04, 'interval: ' + interval + '\nperiod: ' + period,
        transform=ax1.transAxes, fontsize=6, color='gray', alpha=0.5,
        ha='left', va='bottom')

    return plt

# Function to create a Bollinger Bands overlay chart
def overlay_bollinger(dataframe, *args, **kwargs):
    """
    A Bollinger Band is a set of trendlines plotted two standard deviations
    (positively and negatively) away from a simple moving average (SMA) of a
    security's price.
    """

    # keywords & vars
    num_of_std  = kwargs.get('num_of_std', 2)
    window_size = kwargs.get('window_size', 20)

    # plot chart type in title
    plt.title('Bollinger Bands', loc='right', fontsize=8, color='darkblue')

    # create rolling mean and standard deviation
    rolling_mean = dataframe['Close'].rolling(window=window_size).mean()
    rolling_std = dataframe['Close'].rolling(window=window_size).std()

    # create upper and lower bands
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)

    # plot stock data, rolling mean and Bollinger Bands
    plt.plot(rolling_mean, label='Rolling Mean', linewidth=0.5, linestyle='dashed', color='gray')
    plt.plot(upper_band, label='Upper band', linewidth=0.5, color='blue')
    plt.plot(lower_band, label='Lower band', linewidth=0.5, color='purple')

    plt.fill_between(dataframe.index,
        upper_band, lower_band,
        where=upper_band > lower_band,
        color='lightgrey', alpha=0.2)

    # Show legend on the plot
    plt.legend(loc='upper left', fontsize=8)

    return plt

# Function to create an Ichimoku overlay chart.
def overlay_ichimoku(dataframe, *args, **kwargs):
    """
    The Ichimoku chart shows support and resistance levels, as well as other essential
    information such as trend direction and momentum. Compared to standard candlestick
    charts, the Ichimoku Cloud contains more data points, increasing the accuracy of
    forecast price moves.
    """

    # keywords & vars
    base   = kwargs.get('num_of_std', 9)
    period = kwargs.get('window_size', 26)

    # plot chart type in title
    plt.title('Ichimoku Cloud', loc='right', fontsize=8, color='darkblue')

    tenkan_sen = ((dataframe['High'] + dataframe['Low'])/2).rolling(base).mean()
    kijun_sen = ((dataframe['High'] + dataframe['Low'])/2).rolling(period).mean()
    senkou_span_a = ((tenkan_sen + kijun_sen)/2).shift(period)
    senkou_span_b = ((dataframe['High'] + dataframe['Low'])/2).rolling(period).mean().shift(period)
    chikou_span = ((dataframe['High'] + dataframe['Low'])/2).shift(-period)

    dataframe['tenkan_sen'] = tenkan_sen
    dataframe['kijun_sen'] = kijun_sen
    dataframe['senkou_span_a'] = senkou_span_a
    dataframe['senkou_span_b'] = senkou_span_b
    dataframe['chikou_span'] = chikou_span

    # Plot the Ichimoku chart
    plt.plot(dataframe['tenkan_sen'], label='Tenkan-Sen', linewidth=0.5, color='darkorange')
    plt.plot(dataframe['kijun_sen'], label='Kijun-Sen', linewidth=0.5, color='purple')
    plt.plot(dataframe['senkou_span_a'], label='Senkou Span A', linewidth=0.5, alpha=0.05, color='grey')
    plt.plot(dataframe['senkou_span_b'], label='Senkou Span B', linewidth=0.75, color='red')
    plt.plot(dataframe['chikou_span'], label='Chikou Span', linewidth=1, linestyle='dashed', alpha=0.5, color='cyan')

    # Plot Kumo (Cloud)
    plt.fill_between(dataframe.index,
        dataframe['senkou_span_a'], dataframe['senkou_span_b'],
        where=dataframe['senkou_span_a'] >= dataframe['senkou_span_b'],
        color='orange', alpha=0.2)
    plt.fill_between(dataframe.index,
        dataframe['senkou_span_a'], dataframe['senkou_span_b'],
        where=dataframe['senkou_span_a'] < dataframe['senkou_span_b'],
        color='grey', alpha=0.2)

    # Show legend on the plot
    plt.legend(loc='upper left', fontsize=8)

    return plt

# Function to create a VWAP overlay chart.
def overlay_vwap(dataframe):
    """
    VWAP represents the average price a security has traded at throughout the day, based on both volume and price.
    """

    # plot chart type in title
    plt.title('Volume-Weighted Average Price', loc='right', fontsize=8, color='darkblue')

    # create vwap
    dataframe['VWAP'] = (dataframe['Close'] * dataframe['Volume']).cumsum() / dataframe['Volume'].cumsum()

    # plot stock data, rolling mean and Bollinger Bands
    plt.plot(dataframe['VWAP'], label='VWAP', linewidth=0.8, color='blue')

    # Show legend on the plot
    plt.legend(loc='upper left', fontsize=8)

    return plt

if __name__ == "__main__":
    # Initialize logging
    logging.basicConfig(level=logging.DEBUG, encoding="utf-8",
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename='chart.log')

    ticker   = "SPY"
    interval = "15m"
    period   = "14d"

    # Read historical data from Yahoo Finance
    #df = yf.download(ticker, interval=interval, period=period)
    #df.to_csv('~/yf-history.csv')

    # Read the data from the CSV file
    df = pd.read_csv('~/yf-history.csv')

    graph = graph_candlestick(df, ticker=ticker, interval=interval, period=period)
    graph = overlay_bollinger(df)
    #graph = overlay_ichimoku(df)
    #graph = overlay_vwap(df)

    graph.savefig("chart.png", dpi=600, bbox_inches='tight', pad_inches=0.1)
    graph.close()
