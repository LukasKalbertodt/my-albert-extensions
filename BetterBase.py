# -*- coding: utf-8 -*-

"""Converts between bases 2, 8, 10 and 16. Just type your number. If you don't
   use a prefix, the number is interpreted as decimal. For other input bases,
   use the prefixes '0b' for binary, '0o' for octal and '0x' for hexadecimal."""

from albertv0 import *

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "BetterBase"
__version__ = "1.0"
__author__ = "Lukas Kalbertodt"

def handleQuery(query):
    try:
        input = query.rawString

        if input.startswith("0x") or input.startswith("0X"):
            base = 16
        elif input.startswith("0o") or input.startswith("0O"):
            base = 8
        elif input.startswith("0b") or input.startswith("0B"):
            base = 2
        else:
            base = 10

        try:
            value = int(input, base)
        except ValueError:
            # In this case it's not an integer, so we just don't show anything
            return

        items = []
        def add_item(value, base, prefix, subtext):
            # Convert number to string in the specified base
            digits = "0123456789ABCDEF"

            text = ""
            while value != 0:
                digits_index = value % base
                text = digits[digits_index] + text
                value = value // base

            if not text:
                text = "0"

            # Add item
            item = Item(id=__prettyname__, completion=query.rawString)
            item.text = prefix + text
            item.subtext = subtext
            item.addAction(ClipAction("Copy to clipboard", item.text))
            items.append(item)


        if base != 2:
            add_item(value, 2, "0b", "Binary (base 2)")

        if base != 8:
            add_item(value, 8, "0o", "Octal (base 8)")

        if base != 10:
            add_item(value, 10, "", "Decimal (base 10)")

        if base != 16:
            add_item(value, 16, "0x", "Hexadecimal (base 16)")

        return items

    # We never know what could go wrong...
    except Exception as e:
        item = Item(id=__prettyname__, completion=query.rawString)
        item.text = e.__class__.__name__
        item.subtext = str(e)
        return item
