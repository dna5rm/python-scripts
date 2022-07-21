#!/bin/env -S python3

import os, errno
import logging
import netrc
import tempfile
import sys
import pandas as pd
import telegram as tg
import yfinance as yf
import chart

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

            # Read historical data from Yahoo Finance
            df = yf.download(ticker, interval='15m', period='7d')
            df.to_csv(filename + '.csv')

            # Read the data from the CSV file
            df = pd.read_csv(filename + '.csv')

            graph = chart.graph_candlestick(df, ticker=ticker)
            graph = chart.overlay_ichimoku(df, 9, 26)

            graph.savefig(filename + '.png', dpi=600, bbox_inches='tight', pad_inches=0.1)
            graph.close()

            # Send the image to Telegram
            bot = tg.Bot(token=token)
            bot.send_photo(chat_id=chat_id,
                    photo=open(filename + '.png', 'rb'),
                    caption=ticker + ' chart')
        finally:
            for file in [filename, filename + '.csv', filename + '.png']:
                silentremove(file)

    exit(0)
