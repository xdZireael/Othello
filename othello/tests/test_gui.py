import pytest
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # pylint: disable=wrong-import-position

from othello.gui import ListBoxWithLength, OthelloGUI
from unittest.mock import MagicMock


def test_listboxwl():
    listbox = ListBoxWithLength()
    assert len(listbox) == 0
    label1, label2 = Gtk.Label(), Gtk.Label()
    listbox.prepend(label1)
    assert len(listbox) == 1
    listbox.append(label2)
    assert len(listbox) == 2
    listbox.remove(label1)
    assert len(listbox) == 1
