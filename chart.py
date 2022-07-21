#!/bin/env -S python3
""" ichimoki.py - A play script to generate an ichimoku chart. """

# Import packages
import os, logging
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mplfinance.original_flavor import candlestick_ohlc
import numpy as np
import yfinance as yf

# Function to create a candlestick_ohlc chart using mplfinance.
def graph_candlestick(dataframe, *args, **kwargs):
    """
    Graphs a candlestick_ohlc chart using mplfinance.
    """

    # keywords & vars
    ticker = kwargs.get('ticker', '')
    xdate = [dt.datetime.strptime(x[:-6], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d\n%A') for x in dataframe.Datetime]


    plt.figure(figsize=(12,3))
    plt.style.use('bmh')
    plt.title('{}'.format(ticker), loc='left')

    plt.xticks(np.arange(0, len(dataframe), step=28), xdate[::28], rotation=45, fontsize=8)

    #plt.xlabel('Date', fontsize=6)
    #plt.ylabel('Price', fontsize=6, color='grey')

    ax = plt.subplot(1,1,1)

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
    candlestick_ohlc(ax, list(zip(list(plotdata.index.tolist()),
            plotdata["Open"].tolist(),
            plotdata["High"].tolist(),
            plotdata["Low"].tolist(),
            plotdata["Close"].tolist()
        )),
        width = 0.55,
        colorup = "green",
        colordown = "red"
    )

    return plt

# Very rough
def overlay_ichimoku(dataframe, base, period):
    """
    The Ichimoku chart shows support and resistance levels, as well as other essential
    information such as trend direction and momentum. Compared to standard candlestick
    charts, the Ichimoku Cloud contains more data points, increasing the accuracy of
    forecast price moves.
    """

    plt.title('Ichimoku', loc='right', fontsize=8, color='grey')

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
            dataframe['senkou_span_a'],
            dataframe['senkou_span_b'],
            where=dataframe['senkou_span_a'] >= dataframe['senkou_span_b'],
            color='orange', alpha=0.2)
    plt.fill_between(dataframe.index,
            dataframe['senkou_span_a'],
            dataframe['senkou_span_b'],
            where=dataframe['senkou_span_a'] < dataframe['senkou_span_b'],
            color='grey', alpha=0.2)

    # Show legend on the plot
    plt.legend(loc='upper left', fontsize=8)

    return plt

    return plt

if __name__ == "__main__":
# Initialize logging
    logging.basicConfig(level=logging.DEBUG, encoding="utf-8",
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename='ichimoku.log')

    # If the file exists, read it.
if __name__ == "__main__":
# Initialize logging
    logging.basicConfig(level=logging.DEBUG, encoding="utf-8",
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename='ichimoku.log')

    ticker = "PLTR"

    # Read historical data from Yahoo Finance
    #df = yf.download(ticker, interval="15m", period="7d")
    #df.to_csv('~/yf-history.csv')

    # Read the data from the CSV file
    df = pd.read_csv('~/yf-history.csv')

    graph = graph_candlestick(df, ticker=ticker)
    graph = overlay_ichimoku(df, 9, 26)

    graph.savefig('chart.png', dpi=600, bbox_inches='tight', pad_inches=0.1)
    graph.close()
