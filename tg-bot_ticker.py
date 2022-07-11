#!/bin/env -S python3

import os, errno
import logging
import netrc
import tempfile
import sys
import matplotlib.pyplot as plt
#import numpy as np
import pandas as pd
import telegram as tg
import yfinance as yf

# Function to get netrc credentials
def get_netrc_credentials(machine):
    """Fetch netrc credentials."""
    try:
        machine_details = netrc_file.hosts[machine]
        return machine_details[0], machine_details[2]
    except KeyError:
        return None, None

# Function to silently delete a file
def silentremove(filename):
    """Silently delete a file"""
    try:
        os.remove(filename)
    except OSError as e:              # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:   # errno.ENOENT = no such file or directory
            raise                     # re-raise exception if a different error occurred

# Function to create simple data plot
def plot_data_simple(ticker, data, filename):
    """Perform a simple data plot for testing"""
    data.plot("Datetime", ["Open", "High", "Low", "Close"])
    plt.title(ticker + " chart")
    plt.savefig(filename)
    plt.close()

# Function to plot data as a candlestick chart
def plot_data_candlestick(ticker, data, filename):
    """Perform a candlestick chart plot for testing"""
    data.plot("Datetime", ["Open", "High", "Low", "Close"], kind="candlestick")
    plt.title(ticker + " chart")
    plt.savefig(filename)
    plt.close()

if __name__ == "__main__":
    # Initialize logging
    logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=os.path.splitext(os.path.basename(__file__))[0] + ".log",
            encoding='utf-8')

    # Read task from any type of stdin
    if not sys.stdin.isatty():
        stdin = sys.stdin.readlines()
    else:
        stdin = sys.argv[1:]

    # Read in the netrc file
    netrc_file = netrc.netrc()

    # Fetch telegram credentials
    token = get_netrc_credentials('telegram')[1]
    chat_id = get_netrc_credentials('telegram')[0]

    for ticker in stdin:

        img, filename = tempfile.mkstemp()
        try:
            #data = yf.download(ticker, interval="15m", period="7d")
            #data.to_csv(filename + ".csv")

            data = pd.read_csv("~/testdata.csv")

            # Plot the data
            plot_data_candlestick(ticker, data, filename + ".png")

            # Send the image to Telegram
            bot = tg.Bot(token=token)
            bot.send_photo(chat_id=chat_id,
                    photo=open(filename + ".png", 'rb'),
                    caption=ticker + " chart")
        finally:
            for file in [filename, filename + ".csv", filename + ".png"]:
                silentremove(file)

    exit(0)
