"""Fixtures compartilhadas pelos testes."""

import pytest

from src.app import create_app


@pytest.fixture
def app():
    """Aplicação configurada com banco em memória (isolado por teste)."""
    return create_app({"TESTING": True, "DATABASE": ":memory:"})


@pytest.fixture
def client(app):
    """Cliente HTTP de teste do Flask."""
    return app.test_client()


@pytest.fixture
def make_task(client):
    """Atalho para criar uma tarefa via API e devolver o JSON criado."""

    def _make(**fields):
        payload = {"title": "Tarefa de teste", **fields}
        response = client.post("/api/tasks", json=payload)
        assert response.status_code == 201, response.get_json()
        return response.get_json()

    return _make
