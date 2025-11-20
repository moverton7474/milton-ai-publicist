"""
Vercel entrypoint for Milton AI Publicist
This file imports the FastAPI app from dashboard/app.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app from dashboard
from dashboard.app import app

# Export for Vercel
__all__ = ['app']
