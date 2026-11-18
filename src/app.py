"""Aplicação Flask: API REST e interface web do TechFlow Tasks.

Execução local:
    flask --app src.app run --debug

O Flask encontra automaticamente a função ``create_app`` (application factory).
"""

import os

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for

from src.models import PRIORITY_LABELS, STATUS_LABELS, ValidationError, validate_task_data
from src.repository import TaskRepository


def create_app(config: dict = None) -> Flask:
    """Cria e configura a aplicação (padrão *application factory*).

    Receber a configuração por parâmetro permite que os testes usem um
    banco em memória sem afetar o banco real.
    """
    app = Flask(__name__)
    app.config.update(
        DATABASE=os.environ.get("TECHFLOW_DB", "techflow.db"),
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-techflow"),
    )
    if config:
        app.config.update(config)

    repo = TaskRepository(app.config["DATABASE"])
    app.extensions["task_repo"] = repo

    register_api(app, repo)
    register_web(app, repo)
    return app


def register_web(app: Flask, repo: TaskRepository) -> None:
    """Registra as páginas HTML (quadro Kanban e edição de tarefas)."""

    def render_board(errors=None, form=None, status_code=200):
        status_filter = request.args.get("status")
        if status_filter not in STATUS_LABELS:
            status_filter = None
        priority_filter = request.args.get("priority")
        if priority_filter not in PRIORITY_LABELS:
            priority_filter = None
        columns = {
            status: repo.list(status=status, priority=priority_filter)
            for status in STATUS_LABELS
            if status_filter in (None, status)
        }
        return (
            render_template(
                "index.html",
                columns=columns,
                counts=repo.count_by_status(),
                critical_pending=repo.count_critical_pending(),
                status_labels=STATUS_LABELS,
                priority_labels=PRIORITY_LABELS,
                status_filter=status_filter,
                priority_filter=priority_filter,
                errors=errors or {},
                form=form or {},
            ),
            status_code,
        )

    @app.get("/")
    def index():
        return render_board()

    @app.post("/tasks")
    def create_task():
        form = request.form.to_dict()
        try:
            data = validate_task_data(form)
        except ValidationError as exc:
            return render_board(errors=exc.errors, form=form, status_code=400)
        task = repo.create(data)
        flash(f'Tarefa "{task.title}" criada.')
        return redirect(url_for("index"))

    @app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
    def edit_task(task_id):
        task = repo.get(task_id) or abort(404)
        errors = {}
        form = task.to_dict()
        if request.method == "POST":
            form = request.form.to_dict()
            try:
                data = validate_task_data(form)
            except ValidationError as exc:
                errors = exc.errors
            else:
                repo.update(task_id, data)
                flash("Tarefa atualizada.")
                return redirect(url_for("index"))
        return (
            render_template(
                "edit.html",
                task=task,
                form=form,
                errors=errors,
                status_labels=STATUS_LABELS,
                priority_labels=PRIORITY_LABELS,
            ),
            400 if errors else 200,
        )

    @app.post("/tasks/<int:task_id>/move")
    def move_task(task_id):
        """Move o card para outra coluna do quadro (muda o status)."""
        try:
            data = validate_task_data({"status": request.form.get("status")}, partial=True)
        except ValidationError:
            abort(400)
        repo.update(task_id, data) or abort(404)
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/delete")
    def delete_task(task_id):
        if not repo.delete(task_id):
            abort(404)
        flash("Tarefa excluída.")
        return redirect(url_for("index"))


def register_api(app: Flask, repo: TaskRepository) -> None:
    """Registra os endpoints JSON em /api."""

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/tasks")
    def api_list_tasks():
        status = request.args.get("status")
        priority = request.args.get("priority")
        if status and status not in STATUS_LABELS:
            return jsonify(errors={"status": "Status inválido."}), 400
        if priority and priority not in PRIORITY_LABELS:
            return jsonify(errors={"priority": "Prioridade inválida."}), 400
        tasks = repo.list(status=status, priority=priority)
        return jsonify([t.to_dict() for t in tasks])

    @app.post("/api/tasks")
    def api_create_task():
        try:
            data = validate_task_data(request.get_json(silent=True))
        except ValidationError as exc:
            return jsonify(errors=exc.errors), 400
        task = repo.create(data)
        return jsonify(task.to_dict()), 201

    @app.get("/api/tasks/<int:task_id>")
    def api_get_task(task_id):
        task = repo.get(task_id) or abort(404)
        return jsonify(task.to_dict())

    @app.put("/api/tasks/<int:task_id>")
    def api_update_task(task_id):
        try:
            data = validate_task_data(request.get_json(silent=True), partial=True)
        except ValidationError as exc:
            return jsonify(errors=exc.errors), 400
        task = repo.update(task_id, data) or abort(404)
        return jsonify(task.to_dict())

    @app.delete("/api/tasks/<int:task_id>")
    def api_delete_task(task_id):
        if not repo.delete(task_id):
            abort(404)
        return "", 204

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return jsonify(error="Tarefa não encontrada."), 404
        return "Página não encontrada.", 404
