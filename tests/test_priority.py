"""Testes da mudança de escopo v1.1: prioridade das tarefas."""

import sqlite3

import pytest

from src.models import (
    PRIORITY_CRITICAL,
    PRIORITY_MEDIUM,
    STATUS_DONE,
    Task,
    ValidationError,
    validate_task_data,
)
from src.repository import TaskRepository


# ---------- validação ----------
@pytest.mark.parametrize("priority", ["low", "medium", "high", "critical"])
def test_prioridades_validas(priority):
    assert validate_task_data({"title": "Tarefa", "priority": priority})["priority"] == priority


@pytest.mark.parametrize("priority", ["urgente", "", None, 3])
def test_prioridade_invalida(priority):
    with pytest.raises(ValidationError) as exc:
        validate_task_data({"title": "Tarefa", "priority": priority})
    assert "priority" in exc.value.errors


def test_tarefa_critica_pendente():
    assert Task(title="T", priority=PRIORITY_CRITICAL).is_critical_pending is True
    concluida = Task(title="T", priority=PRIORITY_CRITICAL, status=STATUS_DONE)
    assert concluida.is_critical_pending is False
    assert Task(title="T").is_critical_pending is False


# ---------- repositório ----------
def test_prioridade_padrao_e_media():
    repo = TaskRepository(":memory:")
    assert repo.create({"title": "Sem prioridade"}).priority == PRIORITY_MEDIUM


def test_lista_ordenada_por_prioridade():
    repo = TaskRepository(":memory:")
    for title, priority in [("baixa", "low"), ("critica", "critical"), ("alta", "high")]:
        repo.create({"title": title, "priority": priority})
    assert [t.title for t in repo.list()] == ["critica", "alta", "baixa"]


def test_contagem_de_criticas_pendentes():
    repo = TaskRepository(":memory:")
    repo.create({"title": "Crítica aberta", "priority": "critical"})
    repo.create({"title": "Crítica feita", "priority": "critical", "status": "done"})
    repo.create({"title": "Normal"})
    assert repo.count_critical_pending() == 1


def test_migracao_de_banco_da_versao_1_0(tmp_path):
    """Um banco criado antes da mudança (sem a coluna priority) continua funcionando."""
    db = tmp_path / "v1.db"
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, "
        "description TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'todo', "
        "created_at TEXT NOT NULL, updated_at TEXT NOT NULL)"
    )
    conn.execute(
        "INSERT INTO tasks (title, created_at, updated_at) VALUES ('Antiga', 'x', 'x')"
    )
    conn.commit()
    conn.close()

    task = TaskRepository(str(db)).list()[0]
    assert task.title == "Antiga"
    assert task.priority == PRIORITY_MEDIUM


# ---------- API e interface ----------
def test_api_cria_e_filtra_por_prioridade(client, make_task):
    created = make_task(title="Carga perecível", priority="critical")
    assert created["priority_label"] == "Crítica"
    make_task(title="Rotina", priority="low")
    result = client.get("/api/tasks?priority=critical").get_json()
    assert [t["title"] for t in result] == ["Carga perecível"]


def test_api_filtro_de_prioridade_invalido(client):
    assert client.get("/api/tasks?priority=xyz").status_code == 400


def test_api_atualiza_prioridade(client, make_task):
    task = make_task()
    response = client.put(f"/api/tasks/{task['id']}", json={"priority": "high"})
    assert response.get_json()["priority"] == "high"


def test_painel_exibe_criticas_pendentes(client, make_task):
    make_task(title="Urgente", priority="critical")
    html = client.get("/").get_data(as_text=True)
    assert "Críticas pendentes" in html
    assert "task-critical" in html


def test_filtro_de_prioridade_na_interface(client, make_task):
    make_task(title="Alta prioridade", priority="high")
    make_task(title="Baixa prioridade", priority="low")
    html = client.get("/?priority=high").get_data(as_text=True)
    assert "Alta prioridade" in html
    assert "Baixa prioridade" not in html
