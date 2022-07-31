#!/bin/env -S python3
"""
Command a bot to post a stock chart to telegram.
"""

import os
import errno
import logging
import netrc
import tempfile
import sys
import pandas as pd
import telegram as tg
import yfinance as yf
import candlestick_chart as chart

# Function to get netrc credentials
def get_netrc_credentials(machine):
    """Fetch netrc credentials."""

    # Read in the netrc file
    netrc_file = netrc.netrc()

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
    except OSError as os_error:
        if os_error.errno != errno.ENOENT:
            raise

if __name__ == "__main__":
    # Set environment basename for output files
    basename = os.path.splitext(os.path.basename(__file__))[0]

    # Initialize logging
    logfile = os.path.expanduser(f'{basename}.log')
    logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=logfile, encoding='utf-8')

    # Constant Variables
    INTERVAL = "15m"
    PERIOD   = "7d"

    # Read task from any type of stdin
    if not sys.stdin.isatty():
        stdin = sys.stdin.readlines()
    else:
        stdin = sys.argv[1:]

    # Fetch telegram credentials
    token = get_netrc_credentials('telegram')[1]
    chat_id = get_netrc_credentials('telegram')[0]

    for SYMBOL in stdin:

        img, tmpfile = tempfile.mkstemp()
        try:

            # Read historical data from Yahoo Finance
            csvfile = os.path.expanduser(f'{tmpfile}.csv')
            df = yf.download(SYMBOL, interval=INTERVAL, period=PERIOD)
            df.to_csv(csvfile)

            # Read the data from the CSV file
            df = pd.read_csv(csvfile)

            # Plot the data
            graph = chart.graph_candlestick(df, symbol=SYMBOL, interval=INTERVAL, period=PERIOD)
            #graph = chart.overlay_bollinger(df)
            graph = chart.overlay_ichimoku(df)
            #graph = chart.overlay_vwap(df)

            # Save the graph to a temporary file
            pngfile = os.path.expanduser(f'{tmpfile}.png')
            graph.savefig(pngfile, dpi=600, bbox_inches='tight', pad_inches=0.1)
            graph.close()

            # Send the image to Telegram
            bot = tg.Bot(token=token)
            with open(pngfile, 'rb') as photo:
                bot.send_photo(chat_id=chat_id, photo=photo,
                        caption=f'{SYMBOL}: {INTERVAL}, {PERIOD}')

        finally:
            for file in [tmpfile, csvfile, pngfile]:
                silentremove(file)

    sys.exit()
