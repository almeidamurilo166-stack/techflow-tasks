"""Modelo de domínio e regras de validação das tarefas.

Este módulo não depende do Flask nem do banco de dados, o que facilita
os testes unitários: as regras de negócio ficam isoladas aqui.
"""

from dataclasses import dataclass, asdict
from typing import Optional

# Status possíveis de uma tarefa (correspondem às colunas do Kanban).
STATUS_TODO = "todo"
STATUS_DOING = "doing"
STATUS_DONE = "done"

STATUS_LABELS = {
    STATUS_TODO: "A Fazer",
    STATUS_DOING: "Em Progresso",
    STATUS_DONE: "Concluído",
}

# Prioridades (adicionadas na mudança de escopo v1.1 — ver README, seção 9).
# O número define a ordem: quanto maior, mais urgente.
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
PRIORITY_CRITICAL = "critical"

PRIORITY_LABELS = {
    PRIORITY_LOW: "Baixa",
    PRIORITY_MEDIUM: "Média",
    PRIORITY_HIGH: "Alta",
    PRIORITY_CRITICAL: "Crítica",
}
PRIORITY_WEIGHT = {
    PRIORITY_LOW: 1,
    PRIORITY_MEDIUM: 2,
    PRIORITY_HIGH: 3,
    PRIORITY_CRITICAL: 4,
}

TITLE_MIN_LENGTH = 3
TITLE_MAX_LENGTH = 100
DESCRIPTION_MAX_LENGTH = 500


class ValidationError(ValueError):
    """Erro lançado quando os dados de uma tarefa são inválidos.

    O atributo ``errors`` guarda um dicionário {campo: mensagem}, que é
    devolvido ao usuário na API e exibido na interface web.
    """

    def __init__(self, errors: dict):
        super().__init__("Dados de tarefa inválidos")
        self.errors = errors


@dataclass
class Task:
    """Representa uma tarefa do quadro."""

    title: str
    description: str = ""
    status: str = STATUS_TODO
    priority: str = PRIORITY_MEDIUM
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def status_label(self) -> str:
        """Nome do status em português, para exibição."""
        return STATUS_LABELS.get(self.status, self.status)

    @property
    def priority_label(self) -> str:
        """Nome da prioridade em português, para exibição."""
        return PRIORITY_LABELS.get(self.priority, self.priority)

    @property
    def is_critical_pending(self) -> bool:
        """True se a tarefa é crítica e ainda não foi concluída."""
        return self.priority == PRIORITY_CRITICAL and self.status != STATUS_DONE

    def to_dict(self) -> dict:
        """Converte a tarefa em dicionário (usado nas respostas JSON)."""
        data = asdict(self)
        data["status_label"] = self.status_label
        data["priority_label"] = self.priority_label
        return data


def validate_task_data(data: dict, partial: bool = False) -> dict:
    """Valida e normaliza os dados recebidos para criar/editar uma tarefa.

    Args:
        data: dicionário com os campos enviados pelo usuário.
        partial: se True (edição parcial), campos ausentes não são obrigatórios.

    Returns:
        Dicionário apenas com os campos válidos e já normalizados
        (por exemplo, com espaços extras removidos).

    Raises:
        ValidationError: se algum campo for inválido.
    """
    if not isinstance(data, dict):
        raise ValidationError({"_": "O corpo da requisição deve ser um objeto JSON."})

    errors = {}
    clean = {}

    # --- título (obrigatório na criação) ---
    if "title" in data or not partial:
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            errors["title"] = "O título é obrigatório."
        else:
            title = title.strip()
            if len(title) < TITLE_MIN_LENGTH:
                errors["title"] = f"O título deve ter pelo menos {TITLE_MIN_LENGTH} caracteres."
            elif len(title) > TITLE_MAX_LENGTH:
                errors["title"] = f"O título deve ter no máximo {TITLE_MAX_LENGTH} caracteres."
            else:
                clean["title"] = title

    # --- descrição (opcional) ---
    if "description" in data:
        description = data.get("description")
        if description is None:
            description = ""
        if not isinstance(description, str):
            errors["description"] = "A descrição deve ser um texto."
        elif len(description.strip()) > DESCRIPTION_MAX_LENGTH:
            errors["description"] = (
                f"A descrição deve ter no máximo {DESCRIPTION_MAX_LENGTH} caracteres."
            )
        else:
            clean["description"] = description.strip()

    # --- status (opcional; padrão "todo") ---
    if "status" in data:
        status = data.get("status")
        if status not in STATUS_LABELS:
            opcoes = ", ".join(STATUS_LABELS)
            errors["status"] = f"Status inválido. Use um destes: {opcoes}."
        else:
            clean["status"] = status

    # --- prioridade (opcional; padrão "medium") ---
    if "priority" in data:
        priority = data.get("priority")
        if priority not in PRIORITY_LABELS:
            opcoes = ", ".join(PRIORITY_LABELS)
            errors["priority"] = f"Prioridade inválida. Use uma destas: {opcoes}."
        else:
            clean["priority"] = priority

    if errors:
        raise ValidationError(errors)
    return clean
