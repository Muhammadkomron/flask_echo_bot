#!/usr/bin/env python3
"""
WSGI Entry Point for Telegram Echo Bot
This file serves as the entry point for WSGI servers like Gunicorn or uWSGI.
"""

from bot import app

# WSGI application object
application = app

if __name__ == "__main__":
    # This allows running the WSGI file directly for testing
    application.run()
