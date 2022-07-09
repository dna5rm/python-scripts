#!/usr/bin/env python

""" ROT32 a string using Python. """

import sys
ROT32_STRING = ""

#print(sys.version)

if not sys.stdin.isatty():
    message = sys.stdin.readlines()
else:
    message = sys.argv[1:]

#print(message)

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
    return ROT32_STRING


for line in message:
    print(rot32(line), end='')
