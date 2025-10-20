"""
Start Milton Dashboard on Port 8081
(Use this if port 8080 is already in use)
"""

import os
import sys

# Set port to 8081
os.environ["DASHBOARD_PORT"] = "8081"

# Change to dashboard directory
dashboard_dir = os.path.join(os.path.dirname(__file__), "dashboard")
sys.path.insert(0, os.path.dirname(__file__))

# Import and run the app
from dashboard import app as dashboard_app

if __name__ == "__main__":
    import uvicorn

    print("="*70)
    print("MILTON AI PUBLICIST - DASHBOARD")
    print("="*70)
    print()
    print("Starting on http://localhost:8081")
    print("(Port 8081 because 8080 is in use)")
    print()
    print("Press Ctrl+C to stop")
    print("="*70)
    print()

    uvicorn.run(dashboard_app.app, host="0.0.0.0", port=8081)
