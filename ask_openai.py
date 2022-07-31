#!/bin/env -S python3
"""
OpenAI query & response script.

Example ~/.netrc file:
machine openai login api_key password sk-FyXXX...
"""

import logging
import netrc
import os
import sys
import textwrap
import openai
from openai.api_resources import model

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

# Function to ask OpenAI a question
def get_openai_text(task, **kwargs):
    """ OpenAI query for task. """

    # keywords & vars
    model = kwargs.get('model', 'code-davinci-002')

    # Get OpenAI credentials
    openai.api_key = get_netrc_credentials("openai")[1]

    if openai.api_key is None:
        print("No OpenAI credentials found.")
        sys.exit(1)

    # Get OpenAI response
    # https://beta.openai.com/docs/models/gpt-3
    else:
        logging.info("OpenAi task: %s", task)
        response = openai.Completion.create(
            model=model,
            prompt=task,
            temperature=0.7,
            max_tokens=1900,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0)

    return response.choices[0].text

if __name__ == "__main__":
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

    # Get OpenAI response
    if (openai.api_key != 'None') and (message != []):
        text = get_openai_text(message, model='text-davinci-002')
        logging.info(text)
        print(text)
    else:
        print(basename + textwrap.dedent("""
        No query string to send to OpenAi...

        Example:
        $ ask_openai.py "Write ansible task to Ensure HTTP server is not enabled using REL 8 CIS benckmark"
        """))
        sys.exit(1)
