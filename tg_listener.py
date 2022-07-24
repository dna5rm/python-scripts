#!/bin/env -S python3
"""
Listen for a command in a telegram channel
"""

import telegram
from tg_ticker import get_netrc_credentials

# Fetch telegram credentials
token = get_netrc_credentials('telegram')[1]
chat_id = get_netrc_credentials('telegram')[0]

print(token)
