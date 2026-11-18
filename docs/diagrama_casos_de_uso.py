import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch

out = sys.argv[1]
fig, ax = plt.subplots(figsize=(13, 11))
ax.set_xlim(0, 130); ax.set_ylim(0, 110); ax.axis("off")
ax.text(65, 107, "Diagrama de Casos de Uso — TechFlow Tasks (v1.1)", ha="center", fontsize=16)

# Fronteira do sistema
ax.add_patch(FancyBboxPatch((30, 4), 70, 98, boxstyle="round,pad=0.4,rounding_size=2",
                            fc="#f8fafc", ec="#334155", lw=1.5))
ax.text(65, 99, "Sistema TechFlow Tasks", ha="center", fontsize=12, weight="bold")

def actor(x, y, name):
    ax.add_patch(plt.Circle((x, y + 6), 1.6, fc="white", ec="black", lw=1.5))
    ax.plot([x, x], [y + 4.4, y], color="black", lw=1.5)
    ax.plot([x - 3, x + 3], [y + 3, y + 3], color="black", lw=1.5)
    ax.plot([x, x - 2.5], [y, y - 4], color="black", lw=1.5)
    ax.plot([x, x + 2.5], [y, y - 4], color="black", lw=1.5)
    ax.text(x, y - 7, name, ha="center", fontsize=10.5, weight="bold")
    return (x, y + 2)

UC = {}
def uc(key, x, y, text, new=False, w=26, h=7):
    ec = "#be123c" if new else "#1e3a8a"
    fc = "#fff1f2" if new else "#eef2ff"
    ax.add_patch(Ellipse((x, y), w, h, fc=fc, ec=ec, lw=1.4))
    ax.text(x, y, text, ha="center", va="center", fontsize=9.5)
    UC[key] = (x, y, w, h)

def edge_point(key, toward):
    import math
    x, y, w, h = UC[key]
    dx, dy = toward[0] - x, toward[1] - y
    t = 1 / math.sqrt((dx / (w / 2)) ** 2 + (dy / (h / 2)) ** 2)
    return (x + dx * t, y + dy * t)

def assoc(a, key):
    x, y, w, h = UC[key]
    p = (x - w / 2, y) if a[0] < x else (x + w / 2, y)
    ax.plot([a[0], p[0]], [a[1], p[1]], color="#475569", lw=1)

def dep(k1, k2, label):
    p1 = edge_point(k1, UC[k2][:2]); p2 = edge_point(k2, UC[k1][:2])
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="->", ls="--", color="#475569", lw=1))
    ax.text((p1[0] + p2[0]) / 2 + 0.8, (p1[1] + p2[1]) / 2, label, fontsize=8,
            style="italic", color="#334155")

# Casos de uso (coluna esquerda = operação; direita = apoio)
uc("criar", 50, 93, "Criar tarefa")
uc("ver", 50, 83, "Visualizar quadro Kanban")
uc("mover", 50, 73, "Mover tarefa entre colunas")
uc("editar", 50, 63, "Editar tarefa")
uc("excluir", 50, 53, "Excluir tarefa")
uc("filtrar", 50, 43, "Filtrar por status")
uc("prio", 50, 33, "Definir prioridade\n«mudança de escopo»", new=True)
uc("painel", 50, 21, "Consultar painel\nde indicadores")
uc("criticas", 50, 9, "Acompanhar tarefas\ncríticas pendentes", new=True)
uc("validar", 85, 78, "Validar dados\nda tarefa", w=22)
uc("api", 85, 40, "Integrar via\nAPI REST", w=22)

membro = actor(12, 64, "Membro da equipe")
gestor = actor(12, 16, "Gestor de projetos")
sistema = actor(119, 40, "Sistema externo")

for k in ["criar", "ver", "mover", "editar", "excluir", "filtrar", "prio"]:
    assoc(membro, k)
for k in ["painel", "criticas"]:
    assoc(gestor, k)
assoc(sistema, "api")

# Generalização: gestor é um membro da equipe
ax.annotate("", xy=(12, 50.5), xytext=(12, 25.5),
            arrowprops=dict(arrowstyle="-|>,head_length=1.2,head_width=0.6",
                            color="black", lw=1.2, fc="white"))
ax.text(13.5, 38, "generalização", fontsize=8, style="italic", color="#334155")

dep("criar", "validar", "«include»")
dep("editar", "validar", "«include»")
dep("criticas", "painel", "«extend»")

# Legenda
ax.add_patch(Ellipse((108, 100), 8, 3.5, fc="#fff1f2", ec="#be123c"))
ax.text(113, 100, "adicionado na\nmudança de escopo", fontsize=8, va="center")
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
