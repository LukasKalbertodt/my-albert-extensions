# -*- coding: utf-8 -*-

"""TODO"""

import cgi
from Xlib.display import Display
from Xlib import X
from albertv0 import *
from subprocess import call

__iid__ = "PythonInterface/v0.2"
__prettyname__ = "WinSwitch"
__version__ = "1.0"
__author__ = "Lukas Kalbertodt"
__trigger__ = "win"

def handleQuery(query):
    if not query.isTriggered:
        return []

    try:
        items = []

        # Prepare query string
        input = query.string
        needles = cgi.escape(input.lower()).split(' ')

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

                # Add the item
                def activate_win(id):
                    call(['xdotool', 'windowactivate', str(id)])

                item = Item(id=__prettyname__, completion=query.rawString)
                item.text = name#cgi.escape(str(type(name)))
                item.subtext = "Switch <b>to</b>"
                item.addAction(FuncAction("Switch to", lambda id=id: activate_win(id)))
                items.append(item)

        return items

    # We never know what could go wrong...
    except Exception as e:
        item = Item(id=__prettyname__, completion=query.rawString)
        item.text = e.__class__.__name__
        item.subtext = str(e)
        return item
