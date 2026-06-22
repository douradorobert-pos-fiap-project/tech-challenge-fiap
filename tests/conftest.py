import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.dependencies import get_session
from src.api.main import app
from src.infrastructure.database.base import Base
from src.infrastructure.auth.jwt_handler import create_access_token

# Import all models so Base.metadata knows about them
from src.infrastructure.database.models.cliente_model import ClienteModel  # noqa: F401
from src.infrastructure.database.models.veiculo_model import VeiculoModel  # noqa: F401
from src.infrastructure.database.models.servico_model import ServicoModel  # noqa: F401
from src.infrastructure.database.models.peca_model import PecaModel  # noqa: F401
from src.infrastructure.database.models.ordem_servico_model import (  # noqa: F401
    ItemPecaModel,
    ItemServicoModel,
    OrdemServicoModel,
)


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_session(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(test_session):
    def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_token():
    return create_access_token(data={"sub": "admin", "role": "admin"})


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
