#!/bin/env -S python3
"""
Listen for a command in a telegram channel
"""

import os
import sys
import csv
import time
import telegram
from tg_ticker import get_netrc_credentials
from ask_openai import get_openai_text

# Fetch telegram credentials
token = get_netrc_credentials('telegram')[1]

# using the telegram bot api to receive messages in a telegram channel
bot = telegram.Bot(token=token)
print(f"{bot.get_me()}")
running = True

while running == True:
    # using the telegram bot api to recieve messages
    for update in bot.getUpdates():

        try:
            # if entities.type == 'bot_command' then send a message to the telegram channel
            if (update.message.entities[0].type == 'bot_command') and (update.message.chat.type == 'private'):

                # if csv file does not exist, create it
                if not os.path.isfile(f"tg_{update.message.chat_id}.log"):
                    with open(f"tg_{update.message.chat_id}.log", "w") as f:
                        f.write("date,username,message_id,text\n")
                        f.close()

                # check if message_id is already in the csv file
                with open(f"tg_{update.message.chat_id}.log", 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row[2] == str(update.message.message_id):
                            # Do nothing!
                            break
                    else:
                        # if message_id is not in the csv file, then add it and process text
                        with open(f"tg_{update.message.chat_id}.log", 'a') as f:
                            print(f"{update}")
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
                            elif update.message.text == '/chart':
                                bot.sendMessage(chat_id=update.message.chat_id, text="chart!")

                            # Command is requesting to stop the bot.
                            elif update.message.text == '/die':
                                running = False
                                break

                    # Close the csv file and sleep for 5 seconds
                    f.closed()

        except:
            # Do nothing!
            pass

    #print("Sleeping for 5 seconds...")
    time.sleep(5)
