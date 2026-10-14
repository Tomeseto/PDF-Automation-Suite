"""PDF Automation Suite — main entry point."""

import sys
import threading
import time
import webbrowser
import uvicorn

# Ensure UTF-8 output on Windows consoles if supported
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def open_browser(url: str, delay: float = 1.2) -> None:
    """Open default web browser after a short delay to allow server startup."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main() -> None:
    """Launch the PDF Automation Suite."""
    # Optional fallback to legacy CustomTkinter GUI if requested
    if "--gui" in sys.argv:
        import customtkinter as ctk
        from app.gui.app_window import AppWindow

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        app = AppWindow()
        app.mainloop()
        return

    # Default: Launch modern iLovePDF-style localhost web application
    host = "127.0.0.1"
    port = 8088
    url = f"http://{host}:{port}"

    print("=" * 60)
    print("  [PDF Automation Suite - iLovePDF Local]")
    print(f"  Running locally at: {url}")
    print("  100% Offline & Private (All processing runs locally)")
    print("=" * 60)

    # Automatically launch default browser in background
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    # Run Uvicorn server
    uvicorn.run("app.web.server:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
