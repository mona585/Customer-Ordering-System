# wsgi.py
"""WSGI entry point for production servers (gunicorn, etc.)"""

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from app import create_app

# Create app instance for WSGI servers
app = create_app('production')

if __name__ == '__main__':
    app.run()
