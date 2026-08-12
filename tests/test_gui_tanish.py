"""Tests for Tanish's GUI views."""

import customtkinter as ctk
import pytest

from app.gui.views.conversion_view import ConversionView

def test_conversion_view_init():
    root = ctk.CTk()
    view = ConversionView(root)
    assert view is not None
    root.destroy()
