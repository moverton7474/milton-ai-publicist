"""
Vercel entrypoint for Milton AI Publicist
This file imports the FastAPI app from dashboard/app.py

Vercel expects a FastAPI application instance named 'app' in this module.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# Ensure we're in the correct working directory
if os.getcwd() != str(current_dir):
    os.chdir(current_dir)

# Import the FastAPI app from dashboard
# This is the main application instance that Vercel will serve
from dashboard.app import app

# Explicitly export 'app' for Vercel
__all__ = ['app']
