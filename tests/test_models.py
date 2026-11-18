"""Testes unitários das regras de validação (src/models.py)."""

import pytest

from src.models import (
    STATUS_DONE,
    STATUS_TODO,
    Task,
    ValidationError,
    validate_task_data,
)


def test_dados_validos_sao_normalizados():
    clean = validate_task_data({"title": "  Planejar sprint  ", "description": " Reunião "})
    assert clean == {"title": "Planejar sprint", "description": "Reunião"}


def test_titulo_obrigatorio_na_criacao():
    with pytest.raises(ValidationError) as exc:
        validate_task_data({"description": "sem título"})
    assert "title" in exc.value.errors


@pytest.mark.parametrize("titulo", ["", "   ", None, 123])
def test_titulo_vazio_ou_de_tipo_errado_e_rejeitado(titulo):
    with pytest.raises(ValidationError) as exc:
        validate_task_data({"title": titulo})
    assert exc.value.errors["title"] == "O título é obrigatório."


def test_titulo_curto_demais():
    with pytest.raises(ValidationError) as exc:
        validate_task_data({"title": "ab"})
    assert "pelo menos 3" in exc.value.errors["title"]


def test_titulo_longo_demais():
    with pytest.raises(ValidationError) as exc:
        validate_task_data({"title": "x" * 101})
    assert "no máximo 100" in exc.value.errors["title"]


def test_titulo_no_limite_e_aceito():
    assert validate_task_data({"title": "x" * 100})["title"] == "x" * 100


def test_descricao_longa_demais():
    with pytest.raises(ValidationError) as exc:
        validate_task_data({"title": "Tarefa", "description": "y" * 501})
    assert "description" in exc.value.errors


def test_descricao_nula_vira_texto_vazio():
    assert validate_task_data({"title": "Tarefa", "description": None})["description"] == ""


def test_status_invalido():
    with pytest.raises(ValidationError) as exc:
        validate_task_data({"title": "Tarefa", "status": "arquivada"})
    assert "status" in exc.value.errors


def test_status_valido():
    assert validate_task_data({"title": "Tarefa", "status": STATUS_DONE})["status"] == STATUS_DONE


def test_validacao_parcial_nao_exige_titulo():
    assert validate_task_data({"status": STATUS_DONE}, partial=True) == {"status": STATUS_DONE}


def test_varios_erros_sao_reportados_juntos():
    with pytest.raises(ValidationError) as exc:
        validate_task_data({"title": "", "status": "x"})
    assert set(exc.value.errors) == {"title", "status"}


def test_corpo_que_nao_e_objeto_e_rejeitado():
    with pytest.raises(ValidationError):
        validate_task_data(["não", "é", "dict"])


def test_task_to_dict_inclui_rotulo_do_status():
    data = Task(title="Tarefa", status=STATUS_TODO).to_dict()
    assert data["status_label"] == "A Fazer"
    assert data["title"] == "Tarefa"
