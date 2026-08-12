"""Tests for Nishit's GUI views."""

import customtkinter as ctk
import pytest

from app.gui.views.security_view import SecurityView

def test_security_view_init():
    root = ctk.CTk()
    view = SecurityView(root)
    assert view is not None
    root.destroy()
