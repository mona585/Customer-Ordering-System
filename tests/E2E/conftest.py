# tests/E2E/conftest.py
import pytest
import threading
from app import create_app
from app.extensions import db
from app.bootstrap.rbac import ensure_rbac_initialized


@pytest.fixture(scope="session")
def base_url():  
    app = create_app("testing")
    with app.app_context():
        db.drop_all()
        db.create_all()
        ensure_rbac_initialized()

    thread = threading.Thread(
        target=lambda: app.run(port=5001, use_reloader=False, use_debugger=False)
    )
    thread.daemon = True
    thread.start()

    yield "http://localhost:5001"