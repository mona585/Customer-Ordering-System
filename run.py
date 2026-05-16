# run.py
"""Development server entry point"""

import sys


def _check_dependencies() -> None:
    """Python 3.13 needs SQLAlchemy >= 2.0.36."""
    if sys.version_info < (3, 13):
        return
    try:
        import sqlalchemy
    except ImportError:
        return
    parts = sqlalchemy.__version__.split(".")
    major, minor = int(parts[0]), int(parts[1])
    patch = int(parts[2].split("+")[0]) if len(parts) > 2 else 0
    if (major, minor, patch) < (2, 0, 36):
        print(
            "ERROR: Python 3.13 requires SQLAlchemy >= 2.0.36.\n"
            'Fix: pip install "SQLAlchemy>=2.0.36"'
        )
        sys.exit(1)


from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

_check_dependencies()

from app import create_app

app = create_app('development')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
