"""
Simple script to run Milton Dashboard on port 8081
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ["DASHBOARD_PORT"] = "8081"

# Now import and run uvicorn
import uvicorn

print("="*70)
print("MILTON AI PUBLICIST - DASHBOARD")
print("="*70)
print()
print("Starting on: http://localhost:8081")
print("(Port 8081 because 8080 is in use)")
print()
print("Open your browser to: http://localhost:8081")
print()
print("Press Ctrl+C to stop")
print("="*70)
print()

# Import the app
from dashboard.app import app

# Run the server
uvicorn.run(app, host="0.0.0.0", port=8081)
