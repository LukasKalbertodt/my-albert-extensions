# -*- coding: utf-8 -*-

"""Searches for a Unicode character by name. By pressing enter, you can copy
   the character in your clipboard. Your search string is split on whitespace
   and each part has to be found in the character name for the character to be
   in the result set. By default, combining characters are not shown. If you
   want to see combining characters, too, include '*' somewhere in your
   input."""

import os
import unicodedata
from albertv0 import *

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "Unicode Search"
__version__ = "1.0"
__author__ = "Lukas Kalbertodt"
__trigger__ = "uni"


iconPath = os.path.dirname(__file__)+"/unicode-logo.svg"

symbols = None

# Loads the file containing all symbols
def initialize():
    global symbols

    def parse_line(line):
        split = line.split("\t")
        return split[0], split[1]

    path = os.path.join(os.path.split(__file__)[0], 'symbols.txt');

    with open(path, encoding='utf-8') as f:
        symbols = [parse_line(line) for line in f.read().splitlines() if line]



def handleQuery(query):
    if not query.isTriggered:
        return []

    try:
        results = []

        # Split the input string and check if a `*` marker is in it
        input = query.string
        show_all_results = '*' in input
        input = input.replace("*", "")
        needles = input.lower().split(' ')

        # Really simple linear search through all symbols
        for symbol in symbols:
            # We won't collect infinite results, 500 should certainly be enough
            if len(results) > 500:
                break

            # If the user already typed something new, the query is cancelled
            # and we should just stop wasting resources
            if not query.isValid:
                return []

            # Check if all query words are found in the unicode character name
            found = True
            for needle in needles:
                if needle not in symbol[1]:
                    found = False
                    break

            if found:
                item = Item(id=__prettyname__, completion=query.rawString)

                # If the character is a combining character, we check if the
                # user requested us to show combining characters. If yes, add a
                # `◌` character in front of it to make it look better
                if unicodedata.combining(symbol[0]):
                    if show_all_results:
                        item.text = "◌" + symbol[0]
                    else:
                        continue
                else:
                    item.text = symbol[0]

                item.subtext = symbol[1]
                item.addAction(ClipAction("Copy to clipboard", item.text))
                item.icon = iconPath
                results.append(item)

        return results

    # You never know what could go wrong
    except Exception as e:
        item = Item(id=__prettyname__, completion=query.rawString)
        item.text = e.__class__.__name__
        item.subtext = str(e)
        return item
