"""Tests for Tanmay's GUI views."""

import customtkinter as ctk
import pytest

from app.gui.views.organization_view import OrganizationView
from app.gui.views.batch_view import BatchView
from app.gui.views.logs_view import LogsView
from app.gui.app_window import AppWindow

# We only test instantiation to ensure no syntax/layout errors,
# since full GUI interaction testing is better done manually.

def test_organization_view_init():
    root = ctk.CTk()
    view = OrganizationView(root)
    assert view is not None
    root.destroy()

def test_batch_view_init():
    root = ctk.CTk()
    view = BatchView(root)
    assert view is not None
    root.destroy()

def test_logs_view_init():
    root = ctk.CTk()
    view = LogsView(root)
    assert view is not None
    root.destroy()

def test_app_window_init():
    # Only test if it doesn't block (mainloop not called)
    app = AppWindow()
    assert app is not None
    app.destroy()
