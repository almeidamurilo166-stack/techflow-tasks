"""Testes da camada de persistência (src/repository.py)."""

import pytest

from src.models import STATUS_DOING, STATUS_DONE, STATUS_TODO
from src.repository import TaskRepository


@pytest.fixture
def repo():
    """Repositório em memória: cada teste começa com o banco vazio."""
    return TaskRepository(":memory:")


def test_criar_e_buscar_tarefa(repo):
    task = repo.create({"title": "Configurar CI", "description": "GitHub Actions"})
    assert task.id is not None
    assert task.status == STATUS_TODO
    assert repo.get(task.id).title == "Configurar CI"


def test_buscar_inexistente_retorna_none(repo):
    assert repo.get(999) is None


def test_listar_e_filtrar_por_status(repo):
    repo.create({"title": "Tarefa A"})
    repo.create({"title": "Tarefa B", "status": STATUS_DONE})
    assert len(repo.list()) == 2
    concluidas = repo.list(status=STATUS_DONE)
    assert [t.title for t in concluidas] == ["Tarefa B"]


def test_atualizar_tarefa(repo):
    task = repo.create({"title": "Escrever README"})
    updated = repo.update(task.id, {"status": STATUS_DOING})
    assert updated.status == STATUS_DOING
    assert updated.title == "Escrever README"  # campos não enviados são mantidos


def test_atualizar_inexistente_retorna_none(repo):
    assert repo.update(42, {"title": "Nada"}) is None


def test_excluir_tarefa(repo):
    task = repo.create({"title": "Tarefa temporária"})
    assert repo.delete(task.id) is True
    assert repo.get(task.id) is None
    assert repo.delete(task.id) is False


def test_contagem_por_status(repo):
    repo.create({"title": "Tarefa 1"})
    repo.create({"title": "Tarefa 2"})
    repo.create({"title": "Tarefa 3", "status": STATUS_DONE})
    assert repo.count_by_status() == {STATUS_TODO: 2, STATUS_DOING: 0, STATUS_DONE: 1}


def test_persistencia_em_arquivo(tmp_path):
    db = tmp_path / "tarefas.db"
    TaskRepository(str(db)).create({"title": "Persistida"})
    # Um novo repositório apontando para o mesmo arquivo enxerga a tarefa.
    assert TaskRepository(str(db)).list()[0].title == "Persistida"
