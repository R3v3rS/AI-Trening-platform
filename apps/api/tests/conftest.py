import pytest
from main import create_app
from core.database import Base, engine

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
