#!/bin/env -S python3
"""OpenAI query & response script."""

import logging
import netrc
import os
import sys
import textwrap
import openai

# Set environment basename for output files
basename = os.path.splitext(os.path.basename(__file__))[0]

# Read task from any type of stdin
if not sys.stdin.isatty():
    message = sys.stdin.readlines()
else:
    message = sys.argv[1:]

# Initialize logging
logfile = basename + '.log'
logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.DEBUG)

# Read in the netrc file
netrc_file = netrc.netrc()

# Function to get netrc credentials
def get_netrc_credentials(machine):
    """Fetch netrc credentials."""
    try:
        machine_details = netrc_file.hosts[machine]
        return machine_details[0], machine_details[2]
    except KeyError:
        return None, None

# Function to ask OpenAI a question
def get_openai_text(task):
    """OpenAI query for task."""
    logging.info("OpenAi task: %s", task)
    response = openai.Completion.create(
            model="text-davinci-002",
            prompt=task,
            temperature=0.7,
            max_tokens=1900,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0

            )
    return response.choices[0].text

if __name__ == "__main__":
    # Get netrc credentials for OpenAI
    openai.api_key = get_netrc_credentials(basename)[1]

    # Get OpenAI response
    if (openai.api_key != 'None') and (message != []):
        text = get_openai_text(message)
        logging.info(text)
        print(text)
    else:
        print(basename + textwrap.dedent("""
        No query string to send to OpenAi...

        Example:
        $ ask_openai.py "Write ansible task to Ensure HTTP server is not enabled using REL 8 CIS benckmark"
        """))
        sys.exit(1)
