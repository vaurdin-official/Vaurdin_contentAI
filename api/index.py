import os
import sys

# Ensure Vercel environment flag is set for other files to read
os.environ['VERCEL'] = '1'

# Add parent directory to path so we can import dashboard
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dashboard.app import app

# Vercel needs the app object to be named 'app'
