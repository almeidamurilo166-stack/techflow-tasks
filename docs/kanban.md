# Quadro Kanban — TechFlow Tasks

Quadro mantido no **GitHub Projects** (aba *Projects* do repositório), no layout *Board*,
com as colunas **To Do (A Fazer)**, **In Progress (Em Progresso)** e **Done (Concluído)**.
Cada card é uma *issue* do repositório, o que permite fechá-la automaticamente pelo commit
(`Closes #n`) e rastrear qual código resolveu cada tarefa.

**Política de WIP:** no máximo 2 cards em *In Progress* ao mesmo tempo.

## Cards

| #  | Card                                                         | Sprint | Rótulos                 | Coluna final |
|----|--------------------------------------------------------------|--------|-------------------------|--------------|
| 1  | Criar estrutura do repositório (/src, /tests, /docs)         | 1      | `chore`                 | Done         |
| 2  | Escrever README com objetivo, escopo e metodologia           | 1      | `docs`                  | Done         |
| 3  | Modelar entidade Task e regras de validação                  | 1      | `feature`               | Done         |
| 4  | Testes unitários da validação de entradas                    | 1      | `test`                  | Done         |
| 5  | Persistência em SQLite (CRUD)                                | 2      | `feature`               | Done         |
| 6  | API REST de tarefas                                          | 2      | `feature`               | Done         |
| 7  | Interface web com quadro Kanban                              | 2      | `feature`               | Done         |
| 8  | Testes de integração da API e da interface                   | 2      | `test`                  | Done         |
| 9  | Pipeline de CI com GitHub Actions (flake8 + pytest)          | 3      | `ci`                    | Done         |
| 10 | **Mudança de escopo: prioridade de tarefas**                 | 3      | `feature`, `mudança de escopo` | Done  |
| 11 | Diagramas UML (casos de uso e classes)                       | 3      | `docs`                  | Done         |
| 12 | Documento teórico com prints comentados                      | 3      | `docs`                  | In Progress  |
| 13 | Gravar vídeo pitch (até 4 min)                               | 3      | `docs`                  | In Progress  |
| 14 | Ajustes visuais do cabeçalho *(devolvido ao backlog)*        | —      | `melhoria`              | To Do        |
| 15 | Autenticação de usuários (versão 2.0)                        | —      | `feature`, `backlog`    | To Do        |
| 16 | Exportar relatório de desempenho da equipe (CSV)             | —      | `feature`, `backlog`    | To Do        |

## Como a mudança de escopo aparece no quadro

1. O card **#10 – Mudança de escopo: prioridade de tarefas** foi criado em *To Do* após a
   revisão da Sprint 2, com a justificativa do cliente na descrição.
2. Para respeitar o limite de WIP e o prazo, o card **#14 – Ajustes visuais do cabeçalho**
   saiu da Sprint 3 e voltou para o *backlog* (*To Do*, sem sprint).
3. O card #10 passou para *In Progress* durante a implementação (commits `docs(scope)`,
   `feat(priority)` e `test(priority)`) e para *Done* quando o pipeline de CI ficou verde.

> O script [`scripts/criar_issues.sh`](../scripts/criar_issues.sh) cria todos esses cards
> como issues automaticamente usando o GitHub CLI (`gh`).
