"""Testes de integração da API REST (/api/tasks)."""


def test_health(client):
    assert client.get("/api/health").get_json() == {"status": "ok"}


def test_criar_tarefa(client):
    response = client.post("/api/tasks", json={"title": "Criar Kanban", "description": "Projects"})
    assert response.status_code == 201
    body = response.get_json()
    assert body["id"] == 1
    assert body["status"] == "todo"
    assert body["status_label"] == "A Fazer"


def test_criar_tarefa_invalida_retorna_400(client):
    response = client.post("/api/tasks", json={"title": ""})
    assert response.status_code == 400
    assert "title" in response.get_json()["errors"]


def test_criar_sem_json_retorna_400(client):
    response = client.post("/api/tasks", data="texto", content_type="text/plain")
    assert response.status_code == 400


def test_listar_tarefas(client, make_task):
    make_task(title="Primeira")
    make_task(title="Segunda", status="done")
    assert len(client.get("/api/tasks").get_json()) == 2
    done = client.get("/api/tasks?status=done").get_json()
    assert [t["title"] for t in done] == ["Segunda"]


def test_listar_com_status_invalido_retorna_400(client):
    assert client.get("/api/tasks?status=xyz").status_code == 400


def test_buscar_tarefa(client, make_task):
    task = make_task(title="Buscar")
    assert client.get(f"/api/tasks/{task['id']}").get_json()["title"] == "Buscar"


def test_buscar_inexistente_retorna_404(client):
    response = client.get("/api/tasks/999")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_atualizar_tarefa(client, make_task):
    task = make_task()
    response = client.put(f"/api/tasks/{task['id']}", json={"status": "doing"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "doing"


def test_atualizar_com_dados_invalidos_retorna_400(client, make_task):
    task = make_task()
    response = client.put(f"/api/tasks/{task['id']}", json={"status": "perdida"})
    assert response.status_code == 400


def test_atualizar_inexistente_retorna_404(client):
    assert client.put("/api/tasks/999", json={"title": "Nova"}).status_code == 404


def test_excluir_tarefa(client, make_task):
    task = make_task()
    assert client.delete(f"/api/tasks/{task['id']}").status_code == 204
    assert client.get(f"/api/tasks/{task['id']}").status_code == 404
    assert client.delete(f"/api/tasks/{task['id']}").status_code == 404
