#!/bin/env -S python3
"""
Listen for a command in a telegram channel
"""

import os
import sys
import csv
import time
import errno
import logging
import netrc
import telegram
import pandas
import yfinance
from tempfile import gettempdir

# Local imports
from ask_openai import get_openai_text
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

# Function to post a stock chart to telegram
def get_ticker_data(symbol, **kwargs):
    """Get stock chart by ticker symbol"""

    # keywords & vars
    INTERVAL = kwargs.get('interval', '15m')
    PERIOD = kwargs.get('period', '7d')

    csvfile = os.path.expanduser(f'{gettempdir()}/yfdata_{symbol}_{INTERVAL}-{PERIOD}.csv')

    # Get stock data if data is older than 15minutes
    if not(os.path.exists(csvfile)) or os.stat(csvfile).st_mtime < time.time() - 300:
        # Read historical data from Yahoo Finance
        dataframe = yfinance.download(symbol, interval=INTERVAL, period=PERIOD)
        dataframe.to_csv(csvfile)

    # Load dataframe from csvfile
    dataframe = pandas.read_csv(csvfile)
    return dataframe

if __name__ == '__main__':
    # Set environment basename for output files
    basename = os.path.splitext(os.path.basename(__file__))[0]

    # Initialize logging
    logfile = os.path.expanduser(f'{basename}.log')
    logging.basicConfig(level=logging.INFO,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=logfile, encoding='utf-8')

    # Fetch telegram credentials
    token = get_netrc_credentials('telegram')[1]

    # using the telegram bot api to receive messages in a telegram channel
    bot = telegram.Bot(token=token)
    logging.info(f"{bot.get_me()}")
    last_message_id = None
    RUNNING = True

    while RUNNING:

        # Get updates from telegram
        for update in bot.getUpdates(-1):

            try:
                # if entities.type == 'bot_command' then send a message to the telegram channel
                if (update.message.entities[0].type == 'bot_command'): # and (update.message.chat.type == 'private'):
                    if (last_message_id != update.message.message_id) and (last_message_id is not None):
                        last_message_id = update.message.message_id
                        command = update.message.text.split(' ')[0]
                        logging.info(f"{update}")

                        #print(f"Command: {command}")

                        # Command is a request for status
                        if command == '/status':
                            message=[f"Hi *{update.message.from_user.first_name}*, I'm {bot.get_me().first_name}!",
                                    "---------------------------------------------",
                                    f"I'm running on *{os.uname()[1]}* (*{sys.platform}*)",
                                    f"Python: *{sys.version.partition(' ')[0]}*",
                                    f"Telegram: *{telegram.__version__}*"]

                            bot.sendMessage(chat_id=update.message.chat_id,
                                    text="\n".join(message),
                                    parse_mode=telegram.ParseMode.MARKDOWN)

                        # Command is requesting an OpenAI question.
                        elif command == '/ask':

                            # test if the user has provided a question
                            if len(update.message.text.split(' ')) > 1:
                                message = get_openai_text(update.message.text.split(' ')[1], model='text-davinci-002')
                                bot.sendMessage(chat_id=update.message.chat_id,
                                        text=f"{message}")
                            else:
                                bot.sendMessage(chat_id=update.message.chat_id,
                                        text="Sorry, I don't understand your question.")

                        # Command is requesting a stock chart.
                        elif command == '/chart':
                            if len(update.message.text.split(' ')) > 1:
                                SYMBOL = update.message.text.split(' ')[1].upper()

                                # Default Values
                                CHART = 'vwap'
                                INTERVAL = '15m'
                                PERIOD = '14d'

                                # Parse arguments
                                if len(update.message.text.split(' ')) > 2:
                                    ARGS = update.message.text.split(' ')[2:]

                                    for arg in ARGS:
                                        if arg.startswith('chart'):
                                            if arg.split('=')[1] in ['bollinger', 'ichimoku', 'vwap']:
                                                CHART = arg.split('=')[1]
                                        elif arg.startswith('interval'):
                                            if arg.split('=')[1] in ['1m', '5m', '15m', '30m', '1h', '1d']:
                                                INTERVAL = arg.split('=')[1]
                                        elif arg.startswith('period'):
                                            if arg.split('=')[1] in ['1d', '7d', '14d', '1w', '1m', '3m', '1y']:
                                                PERIOD = arg.split('=')[1]

                                # Get stock data
                                print(f"Fetching data for {SYMBOL} {INTERVAL}-{PERIOD}")
                                dataframe = get_ticker_data(SYMBOL, interval=INTERVAL, period=PERIOD)

                                # Plot stock data
                                if dataframe is not None:

                                    # Create graph and overlay
                                    graph = chart.graph_candlestick(dataframe, symbol=SYMBOL, interval=INTERVAL, period=PERIOD)
                                    if CHART == 'bollinger':
                                        graph = chart.overlay_bollinger(dataframe)
                                    elif CHART == 'ichimoku':
                                        graph = chart.overlay_ichimoku(dataframe)
                                    else:
                                        graph = chart.overlay_vwap(dataframe)

                                    # Save graph to file
                                    graph.savefig(f'{gettempdir()}/chart_{SYMBOL}_{INTERVAL}-{PERIOD}.png',
                                            dpi=600, bbox_inches='tight', pad_inches=0.1)
                                    graph.close()

                                    # Send graph to telegram
                                    with open(f'{gettempdir()}/chart_{SYMBOL}_{INTERVAL}-{PERIOD}.png', 'rb') as photo:
                                        bot.sendPhoto(chat_id=update.message.chat_id, photo=photo,
                                                caption=f"{SYMBOL} chart={CHART} interval={INTERVAL} period={PERIOD}")

                                else:
                                    bot.sendMessage(chat_id=update.message.chat_id,
                                            text=f"Sorry, I don't understand your request.")
                            else:
                                bot.sendMessage(chat_id=update.message.chat_id,
                                        text="Missing arguments. Please use /chart <symbol> <args>")

                        # Command is requesting to stop the bot.
                        elif command == '/die':
                            RUNNING = False
                            bot.sendMessage(chat_id=update.message.chat_id,
                                    text="Bye!")

                    else:
                        last_message_id = update.message.message_id
            except:
                # Do nothing!
                pass

        # Be nice to the telegram API and sleep for 5 seconds
        time.sleep(5)
