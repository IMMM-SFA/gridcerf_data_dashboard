#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from definitions import PORT

# -----------------------------------------------------------------------------
# App runs here. Define configurations, proxies, etc.
# -----------------------------------------------------------------------------

# server = app.server 
# from app import server as application # in the wsgi.py file -- this targets the Flask server of Dash app

if __name__ == "__main__":
	
	# app = create_app()
	app.run_server(port=PORT, debug=True)
	# app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter
