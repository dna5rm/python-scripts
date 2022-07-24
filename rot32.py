#!/bin/env -S python3
""" Convert a string to rot13. """

import sys

# Convert a string to rot32.
def rot32(string):
    """ Return rot32 of a string. """
    for character in str(string):
        ord_val = (ord(character.lower()))
        if not chr(ord_val).isalpha():
            print(character, end='')
        elif ord_val <= 109:
            print((chr(ord_val+13)), end='')
        else:
            print((chr(ord_val-13)), end='')
    return string

if __name__ == "__main__":

    # Take in a string from the command line
    if not sys.stdin.isatty():
        message = sys.stdin.readlines()
    else:
        message = sys.argv[1:]

    # Convert a string to rot32.
    for line in message:
        rot32(line)

    sys.exit(0)
