"""Testes das páginas HTML (quadro Kanban e formulários)."""


def test_pagina_inicial_exibe_colunas(client):
    html = client.get("/").get_data(as_text=True)
    for coluna in ("A Fazer", "Em Progresso", "Concluído"):
        assert coluna in html


def test_criar_tarefa_pelo_formulario(client):
    response = client.post("/tasks", data={"title": "Pelo formulário"}, follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Pelo formulário" in html
    assert "criada" in html  # mensagem de confirmação


def test_formulario_invalido_mostra_erro(client):
    response = client.post("/tasks", data={"title": "x"})
    assert response.status_code == 400
    assert "pelo menos 3 caracteres" in response.get_data(as_text=True)


def test_mover_tarefa_entre_colunas(client, make_task):
    task = make_task()
    client.post(f"/tasks/{task['id']}/move", data={"status": "done"})
    assert client.get(f"/api/tasks/{task['id']}").get_json()["status"] == "done"


def test_mover_para_status_invalido_retorna_400(client, make_task):
    task = make_task()
    assert client.post(f"/tasks/{task['id']}/move", data={"status": "x"}).status_code == 400


def test_editar_tarefa(client, make_task):
    task = make_task(title="Antes")
    assert client.get(f"/tasks/{task['id']}/edit").status_code == 200
    client.post(
        f"/tasks/{task['id']}/edit",
        data={"title": "Depois", "description": "", "status": "doing"},
    )
    updated = client.get(f"/api/tasks/{task['id']}").get_json()
    assert updated["title"] == "Depois"
    assert updated["status"] == "doing"


def test_editar_com_erro_permanece_na_pagina(client, make_task):
    task = make_task()
    response = client.post(f"/tasks/{task['id']}/edit", data={"title": "", "status": "todo"})
    assert response.status_code == 400
    assert "obrigatório" in response.get_data(as_text=True)


def test_excluir_tarefa_pelo_botao(client, make_task):
    task = make_task()
    client.post(f"/tasks/{task['id']}/delete")
    assert client.get(f"/api/tasks/{task['id']}").status_code == 404


def test_filtro_por_status(client, make_task):
    make_task(title="Só a fazer")
    make_task(title="Já concluída", status="done")
    html = client.get("/?status=done").get_data(as_text=True)
    assert "Já concluída" in html
    assert "Só a fazer" not in html


def test_editar_inexistente_retorna_404(client):
    assert client.get("/tasks/999/edit").status_code == 404
