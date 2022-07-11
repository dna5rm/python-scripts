#!/bin/env -S python3
""" ichimoki.py - A play script to generate an ichimoku chart. """

# Import packages
import os, logging
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf


# This is what I have been working on... Very rough
def ichimoku_cloud(dataframe, base, period, title):
    """
    The Ichimoku chart shows support and resistance levels, as well as other essential
    information such as trend direction and momentum. Compared to standard candlestick
    charts, the Ichimoku Cloud contains more data points, increasing the accuracy of
    forecast price moves.
    """

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

    plt.figure(figsize=(16,9))

    plt.style.use('bmh')

    plt.plot(dataframe['tenkan_sen'], label='Tenkan-Sen')
    plt.plot(dataframe['kijun_sen'], label='Kijun-Sen')
    plt.plot(dataframe['senkou_span_a'], label='Senkou Span A')
    plt.plot(dataframe['senkou_span_b'], label='Senkou Span B')
    plt.plot(dataframe['chikou_span'], label='Chikou Span')

    # Plot Kumo (Cloud)
    plt.fill_between(dataframe.index,
            dataframe['senkou_span_a'],
            dataframe['senkou_span_b'],
            where=dataframe['senkou_span_a'] >= dataframe['senkou_span_b'],
            color='orange', alpha=0.3)
    plt.fill_between(dataframe.index,
            dataframe['senkou_span_a'],
            dataframe['senkou_span_b'],
            where=dataframe['senkou_span_a'] < dataframe['senkou_span_b'],
            color='grey', alpha=0.3)

    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

    plt.savefig('ichimoku.png', dpi=600)
    plt.close()

# Initialize logging
logging.basicConfig(level=logging.DEBUG, encoding="utf-8",
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename='ichimoku.log')


# Read PLTR data
#df = yf.download('PLTR', interval="15m", period="14d")
#df.to_csv("~/ichimoku.csv")
df = pd.read_csv("~/ichimoku.csv")

## Components of Ichimoku ##
# https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/ichimoku-cloud/
# https://www.profitf.com/articles/forex-education/ichimoku-trading/

ichimoku_cloud(df, 9, 26, "Ichimoku Cloud")
