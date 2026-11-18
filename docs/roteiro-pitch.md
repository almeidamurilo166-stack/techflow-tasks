# Roteiro do vídeo pitch (até 4 minutos)

**Antes de gravar:** deixe abertas, em abas separadas, (1) o sistema rodando em
`http://127.0.0.1:5000` com algumas tarefas cadastradas, (2) o repositório no GitHub,
(3) a aba **Projects** com o quadro, (4) a aba **Actions** com uma execução verde e
(5) o terminal na pasta do projeto. Ferramentas de gravação gratuitas: OBS Studio,
Loom ou a Xbox Game Bar do Windows (`Win + Alt + R`).

> Ritmo sugerido: ~140 palavras por minuto. As falas abaixo somam cerca de 3 min 40 s,
> deixando folga para as transições.

| Tempo        | Tela                                         | Fala (sugestão — adapte ao seu jeito) |
|--------------|----------------------------------------------|---------------------------------------|
| 0:00 – 0:20  | README no GitHub                             | "Olá, eu sou [seu nome]. Neste projeto assumi o papel de desenvolvedor e gestor ágil da TechFlow Solutions para criar um sistema de gerenciamento de tarefas para uma startup de logística, que precisa acompanhar o fluxo de trabalho, priorizar tarefas críticas e monitorar a equipe." |
| 0:20 – 0:55  | Aba **Projects** (quadro Kanban)             | "Usei uma abordagem híbrida: Kanban para visualizar o fluxo, com as colunas A Fazer, Em Progresso e Concluído e limite de duas tarefas em andamento, e sprints curtas do Scrum para dar cadência. Cada card é uma issue do repositório. O trabalho foi dividido em três sprints: estrutura e modelo, depois persistência, API e interface, e por fim qualidade e mudança de escopo." |
| 0:55 – 1:45  | Sistema rodando no navegador                 | "Este é o sistema. No topo, o painel mostra quantas tarefas há em cada coluna e quantas críticas estão pendentes. Vou criar uma tarefa… [crie 'Carga refrigerada para Campinas', prioridade Crítica]. Ela entra em A Fazer, já no topo por ser crítica. Posso movê-la para Em Progresso, editar… e excluir. Também filtro por status ou por prioridade. Se eu tentar salvar um título vazio, a validação mostra o erro. Tudo isso também está disponível numa API REST em JSON." |
| 1:45 – 2:25  | Pasta `tests/` e terminal rodando `pytest`   | "A qualidade é garantida por 65 testes automatizados com pytest, em três níveis: testes unitários da validação de entradas, testes da camada de banco de dados e testes de integração, que fazem requisições HTTP reais à API e às páginas, inclusive nos casos de erro. [rode `pytest`] Todos passando, com cobertura acima de 80%." |
| 2:25 – 2:55  | Aba **Actions** → execução verde → detalhes  | "A cada push, o GitHub Actions executa o pipeline: primeiro o flake8 valida o estilo do código; se passar, os testes rodam no Python 3.11 e 3.12. Se alguém enviar código com erro, o pipeline fica vermelho e o problema aparece antes de chegar ao cliente." |
| 2:55 – 3:30  | README seção 9 → card #10 no quadro → commit `feat(priority)` | "Na revisão da segunda sprint, o cliente percebeu que entregas urgentes se misturavam às de rotina. Aceitamos a mudança de escopo: criei o card de prioridade, devolvi um card de menor valor ao backlog para manter o prazo, implementei o campo de prioridade com ordenação, filtro e contador de críticas, e registrei a justificativa e a análise de impacto no README. Os testes garantiram que nada que já funcionava quebrou." |
| 3:30 – 3:55  | Histórico de commits ou tela final           | "Para concluir: a Engenharia de Software transforma um pedido em um produto confiável. Planejamento visível, commits rastreáveis, testes e integração contínua reduzem retrabalho e permitem aceitar mudanças com segurança, que é o que o mercado espera de quem desenvolve software hoje. Obrigado!" |

## Checklist de gravação

- [ ] Duração final abaixo de 4:00
- [ ] Sistema funcionando ao vivo (criar, mover, editar, excluir, filtrar)
- [ ] `pytest` executado na tela
- [ ] Execução verde do GitHub Actions mostrada
- [ ] Mudança de escopo explicada (README + card + commit)
- [ ] Reflexão final sobre Engenharia de Software
- [ ] Vídeo publicado com link acessível (YouTube "Não listado" ou Google Drive com
      "Qualquer pessoa com o link") e link testado em uma janela anônima
