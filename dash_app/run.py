#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from app import app

# -----------------------------------------------------------------------------
# App runs here. Define configurations, proxies, etc.
# -----------------------------------------------------------------------------

# from app import server as application # in the wsgi.py file -- this targets the Flask server of Dash app

if __name__ == "__main__":
	
	port = int(os.environ.get("PORT", 8060))
	app.run_server(port=port, debug=True)
