"""Camada de persistência: guarda as tarefas em um banco SQLite.

Usa apenas a biblioteca padrão (sqlite3), sem ORM, para manter o
projeto simples. Toda a SQL do sistema fica concentrada aqui.
"""

import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

from src.models import (
    PRIORITY_CRITICAL,
    PRIORITY_MEDIUM,
    PRIORITY_WEIGHT,
    STATUS_DONE,
    STATUS_LABELS,
    Task,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    status      TEXT    NOT NULL DEFAULT 'todo',
    priority    TEXT    NOT NULL DEFAULT 'medium',
    created_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL
);
"""

# Expressão SQL que converte a prioridade em número, para ordenar os cards
# do mais urgente para o menos urgente.
PRIORITY_ORDER_SQL = "CASE priority " + " ".join(
    f"WHEN '{name}' THEN {weight}" for name, weight in PRIORITY_WEIGHT.items()
) + " ELSE 0 END"


def _now() -> str:
    """Data/hora atual em UTC no formato ISO 8601."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class TaskRepository:
    """Operações CRUD sobre a tabela ``tasks``."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        # Para ":memory:" mantemos uma única conexão aberta; caso contrário
        # o banco em memória seria perdido a cada nova conexão.
        self._memory_conn = None
        if db_path == ":memory:":
            self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_conn.row_factory = sqlite3.Row
        self.init_schema()

    # ---------- infraestrutura ----------
    def _connect(self) -> sqlite3.Connection:
        if self._memory_conn is not None:
            return self._memory_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _close(self, conn: sqlite3.Connection) -> None:
        if conn is not self._memory_conn:
            conn.close()

    def init_schema(self) -> None:
        conn = self._connect()
        try:
            conn.executescript(SCHEMA)
            self._migrate(conn)
            conn.commit()
        finally:
            self._close(conn)

    @staticmethod
    def _migrate(conn: sqlite3.Connection) -> None:
        """Atualiza bancos criados antes da v1.1 (sem a coluna priority)."""
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(tasks)")}
        if "priority" not in columns:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'"
            )

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> Task:
        return Task(**dict(row))

    # ---------- CRUD ----------
    def create(self, data: dict) -> Task:
        """Cria uma tarefa a partir de dados já validados."""
        now = _now()
        conn = self._connect()
        try:
            cur = conn.execute(
                "INSERT INTO tasks (title, description, status, priority, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    data["title"],
                    data.get("description", ""),
                    data.get("status", "todo"),
                    data.get("priority", PRIORITY_MEDIUM),
                    now,
                    now,
                ),
            )
            conn.commit()
            task_id = cur.lastrowid
        finally:
            self._close(conn)
        return self.get(task_id)

    def get(self, task_id: int) -> Optional[Task]:
        """Busca uma tarefa pelo id. Retorna None se não existir."""
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        finally:
            self._close(conn)
        return self._row_to_task(row) if row else None

    def list(
        self, status: Optional[str] = None, priority: Optional[str] = None
    ) -> List[Task]:
        """Lista as tarefas, opcionalmente filtradas por status e/ou prioridade.

        A ordem é: maior prioridade primeiro e, em caso de empate, as mais recentes.
        """
        sql = "SELECT * FROM tasks"
        conditions, params = [], []
        if status:
            conditions.append("status = ?")
            params.append(status)
        if priority:
            conditions.append("priority = ?")
            params.append(priority)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += f" ORDER BY {PRIORITY_ORDER_SQL} DESC, created_at DESC, id DESC"
        conn = self._connect()
        try:
            rows = conn.execute(sql, params).fetchall()
        finally:
            self._close(conn)
        return [self._row_to_task(r) for r in rows]

    def update(self, task_id: int, data: dict) -> Optional[Task]:
        """Atualiza apenas os campos informados. Retorna None se não existir."""
        if self.get(task_id) is None:
            return None
        fields = ("title", "description", "status", "priority")
        allowed = [field for field in fields if field in data]
        if allowed:
            assignments = ", ".join(f"{field} = ?" for field in allowed)
            values = [data[field] for field in allowed] + [_now(), task_id]
            conn = self._connect()
            try:
                conn.execute(
                    f"UPDATE tasks SET {assignments}, updated_at = ? WHERE id = ?", values
                )
                conn.commit()
            finally:
                self._close(conn)
        return self.get(task_id)

    def delete(self, task_id: int) -> bool:
        """Exclui uma tarefa. Retorna True se algo foi excluído."""
        conn = self._connect()
        try:
            cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            self._close(conn)

    def count_by_status(self) -> dict:
        """Quantidade de tarefas em cada status (usado no painel)."""
        counts = {status: 0 for status in STATUS_LABELS}
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT status, COUNT(*) AS total FROM tasks GROUP BY status"
            ).fetchall()
        finally:
            self._close(conn)
        for row in rows:
            counts[row["status"]] = row["total"]
        return counts

    def count_critical_pending(self) -> int:
        """Quantidade de tarefas críticas que ainda não foram concluídas."""
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT COUNT(*) AS total FROM tasks WHERE priority = ? AND status != ?",
                (PRIORITY_CRITICAL, STATUS_DONE),
            ).fetchone()
        finally:
            self._close(conn)
        return row["total"]
