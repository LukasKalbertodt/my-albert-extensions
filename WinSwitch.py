# -*- coding: utf-8 -*-

"""TODO"""

import cgi
import time
import os
from Xlib.display import Display
from Xlib import X
from albertv0 import *
from subprocess import call
from PIL import Image

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "WinSwitch"
__version__ = "1.0"
__author__ = "Lukas Kalbertodt"
__trigger__ = "win"


def write_png(path, buf, width, height):
    bs = bytearray()

    for i in buf:
        bs.append((i >> 16) & 0xFF)
        bs.append((i >>  8) & 0xFF)
        bs.append((i >>  0) & 0xFF)
        bs.append((i >> 24) & 0xFF)

    img = Image.frombytes("RGBA", (width, height), bytes(bs))
    img.save(path, "png")

def gen_icon(display, id, win):
    # Create cache directory
    base_path = f"{cacheLocation()}/WinSwitch/"
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    # Check if we already have a non-old version of the icon
    path = f"{base_path}/{id}.png"
    if os.path.exists(path):
        if os.path.getmtime(path) + 60 * 60 * 12 >= time.time():
            return path

    # Get icon data. Format is documented here:
    # https://specifications.freedesktop.org/wm-spec/1.3/ar01s05.html
    NET_WM_ICON = display.intern_atom('_NET_WM_ICON')
    res = win.get_full_property(NET_WM_ICON, X.AnyPropertyType)
    arr = res.value

    # Find biggest icon
    max_width = 0
    max_index = 0
    start = 0
    while start < len(arr):
        width = arr[start]
        height = arr[start + 1]

        if width > max_width:
            max_width = width
            max_index = start

        start += width * height + 2


    # Write biggest icon
    width = arr[max_index]
    height = arr[max_index + 1]
    length = width * height
    data = arr[max_index + 2:max_index + 2 + length]

    write_png(path, data, width, height)
    return path



def handleQuery(query):
    if not query.isTriggered:
        return []

    try:
        items = []

        # Prepare query string
        input = query.string
        needles = cgi.escape(input.lower()).strip().split(' ')

        # Create display handle
        display = Display()

        # Intern a few atoms we will use later
        NET_CLIENT_LIST = display.intern_atom('_NET_CLIENT_LIST')
        NET_WM_WINDOW_TYPE = display.intern_atom('_NET_WM_WINDOW_TYPE')
        NET_WM_WINDOW_TYPE_NORMAL = display.intern_atom('_NET_WM_WINDOW_TYPE_NORMAL')
        NET_WM_NAME = display.intern_atom('_NET_WM_NAME')

        # Get the IDs of all windows on the display
        root = display.screen().root
        win_list = root.get_full_property(NET_CLIENT_LIST, X.AnyPropertyType).value

        for id in win_list:
            # If the user already typed something new, the query is cancelled
            # and we should just stop wasting resources
            if not query.isValid:
                return []

            # Get the window associated with that ID
            win = display.create_resource_object('window', id)

            # Check if the window type is "normal window"
            win_type = win.get_full_property(NET_WM_WINDOW_TYPE, X.AnyPropertyType).value[0]
            if win_type == NET_WM_WINDOW_TYPE_NORMAL:
                # Obtain the name of the window. Windows without the `_NET_WM_NAME`
                # property will be ignored
                name = win.get_full_property(NET_WM_NAME, X.AnyPropertyType)
                if not name:
                    continue

                name = name.value.decode('utf-8')

                # Apply filter to the name
                lowercase_name = name.lower()
                is_ok = True
                for needle in needles:
                    if needle not in lowercase_name:
                        is_ok = False
                        break

                if not is_ok:
                    continue

                for needle in needles:
                    start = lowercase_name.find(needle)
                    end = start + len(needle)
                    name = name[:start] + "<b>" + name[start:end] + "</b>" + name[end:]
                    lowercase_name = name.lower()

                # Add the item
                def activate_win(id):
                    call(['xdotool', 'windowactivate', str(id)])

                # Generate icon
                icon_path = gen_icon(display, id, win)

                item = Item(id=__prettyname__, completion=query.rawString)
                item.text = name#cgi.escape(str(type(name)))
                item.subtext = "Switch to"
                item.icon = icon_path
                item.addAction(FuncAction("Switch to", lambda id=id: activate_win(id)))
                items.append(item)

        return items

    # We never know what could go wrong...
    except Exception as e:
        item = Item(id=__prettyname__, completion=query.rawString)
        item.text = e.__class__.__name__
        item.subtext = str(e)
        return item
