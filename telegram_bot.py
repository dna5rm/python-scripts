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

    # If no symbol is provided, return None
    if symbol is None:
        return None
    else:
        # Get stock data if data is older than 15minutes
        if not(os.path.isfile(f'{gettempdir()}/yfdata_{symbol}_{INTERVAL}-{PERIOD}.csv')) \
            or os.stat(f'{gettempdir()}/yfdata_{symbol}_{INTERVAL}-{PERIOD}.csv').st_mtime < time.time() - 300:
                # Read historical data from Yahoo Finance
                csvfile = os.path.expanduser(f'{gettempdir()}/yfdata_{symbol}_{INTERVAL}-{PERIOD}.csv')
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
    RUNNING = True

    while RUNNING:

        # Get updates from telegram
        for update in bot.getUpdates():

            try:
                # if entities.type == 'bot_command' then send a message to the telegram channel
                if (update.message.entities[0].type == 'bot_command') and (update.message.chat.type == 'private'):

                    # if csv file does not exist, create it
                    if not os.path.isfile(f"telegram_{update.message.chat_id}.log"):
                        with open(f"telegram_{update.message.chat_id}.log", "w") as f:
                            f.write("date,username,message_id,text\n")
                            f.close()

                    # check if message_id is already in the csv file
                    with open(f"telegram_{update.message.chat_id}.log", 'r') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if row[2] == str(update.message.message_id):
                                # Do nothing!
                                break
                        else:
                            # if message_id is not in the csv file, then add it and process text
                            with open(f"telegram_{update.message.chat_id}.log", 'a') as f:
                                logging.info(f"{update}")

                                writer = csv.writer(f)
                                writer.writerow([update.message.date, update.message.from_user.username, update.message.message_id, update.message.text])
                                # Command is requesting bot status.
                                if update.message.text == '/status':
                                    message=[f"Hi *{update.message.from_user.first_name}*, I'm {bot.get_me().first_name}!",
                                            "---------------------------------------------",
                                            f"I'm running on *{os.uname()[1]}* (*{sys.platform}*)",
                                            f"Python: *{sys.version.partition(' ')[0]}*",
                                            f"Telegram: *{telegram.__version__}*"]

                                    bot.sendMessage(chat_id=update.message.chat_id,
                                            text="\n".join(message),
                                            parse_mode=telegram.ParseMode.MARKDOWN)

                                # Command is requesting an OpenAI question.
                                elif update.message.text.startswith('/ask'):

                                    # test if the user has provided a question
                                    if len(update.message.text.split(' ')) > 1:
                                        message = get_openai_text(update.message.text.split(' ')[1])
                                        bot.sendMessage(chat_id=update.message.chat_id,
                                                text=f"{message}")
                                    else:
                                        bot.sendMessage(chat_id=update.message.chat_id,
                                                text="Sorry, I don't understand your question.")

                                # Command is requesting a stock chart.
                                elif update.message.text.startswith('/chart'):
                                    SYMBOL = update.message.text.split(' ')[1].upper()

                                    INTERVAL = '15m'
                                    PERIOD = '7d'

                                    print(f"{SYMBOL} {INTERVAL} {PERIOD}")

                                    if SYMBOL > 1:
                                        dataframe = get_ticker_data(SYMBOL)
                                  #      if dataframe is not None:

                                  #          # Plot the data
                                  #          graph = chart.graph_candlestick(dataframe, symbol=SYMBOL, interval=INTERVAL, period=PERIOD)
                                  #          #graph = chart.overlay_bollinger(dataframe)
                                  #          graph = chart.overlay_ichimoku(dataframe)
                                  #          #graph = chart.overlay_vwap(dataframe)

                                  #          # Save the graph to a temporary file
                                  #          graph.savefig(f'{gettempdir()}/chart_{SYMBOL}_{INTERVAL}-{PERIOD}.png',
                                  #                  dpi=600, bbox_inches='tight', pad_inches=0.1)
                                  #         graph.close()

                                  #          # Send the graph to the telegram channel
                                  #          with open(f'{gettempdir()}/chart_{SYMBOL}_{INTERVAL}-{PERIOD}.png', 'rb') as photo:
                                  #              bot.sendPhoto(chat_id=update.message.chat_id,
                                  #                      photo=photo,
                                  #                      caption=f"{SYMBOL} {INTERVAL}-{PERIOD}")

                                    else:
                                        bot.sendMessage(chat_id=update.message.chat_id,
                                                text="Missing the ticker symbol!")

                                # Command is requesting to stop the bot.
                                elif update.message.text == '/die':
                                    RUNNING = False
                                    break

                      # Close the csv file and sleep for 5 seconds
                        f.closed()

            except:
                # Do nothing!
                pass

        # Be nice to the telegram API and sleep for 3 seconds
        time.sleep(3)
