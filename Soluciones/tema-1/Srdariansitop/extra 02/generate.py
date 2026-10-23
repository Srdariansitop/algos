import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

C_INT = "#90caf9"     # nodo interno (comparación)
C_HOJA = "#ffcc80"    # hoja (respuesta)
C_RUTA = "#d32f2f"    # camino resaltado
C_BORDE = "#455a64"
C_GRIS = "#78909c"


# ---------------------------------------------------------------
# Árbol de decisión REAL de la búsqueda binaria (intervalo [lo, hi))
# ---------------------------------------------------------------
def construir(lo, hi, prof=0):
    if lo == hi:
        return {"leaf": True, "ans": lo, "lo": lo, "hi": hi, "d": prof}
    m = lo + (hi - lo) // 2
    return {
        "leaf": False, "m": m, "lo": lo, "hi": hi, "d": prof,
        "no": construir(lo, m, prof + 1),        # A[m] >= x  -> hi = m
        "si": construir(m + 1, hi, prof + 1),    # A[m] <  x  -> lo = m+1
    }


def posiciones(nodo, cont):
    """Hojas en orden de respuesta 0..n (izquierda->derecha)."""
    if nodo["leaf"]:
        nodo["x"] = cont[0]
        cont[0] += 1
    else:
        posiciones(nodo["no"], cont)
        posiciones(nodo["si"], cont)
        nodo["x"] = (nodo["no"]["x"] + nodo["si"]["x"]) / 2


def altura(nodo):
    return nodo["d"] if nodo["leaf"] else max(altura(nodo["no"]), altura(nodo["si"]))


def en_ruta(nodo, ans):
    return ans is not None and nodo["lo"] <= ans <= nodo["hi"]


def dibujar_arbol(ax, raiz, ans=None, fs=11):
    DY = 1.5

    def rec(nodo):
        if nodo["leaf"]:
            return
        for lado, etiqueta in (("no", "no (A[m] ≥ x)"), ("si", "sí (A[m] < x)")):
            h = nodo[lado]
            ruta = en_ruta(nodo, ans) and en_ruta(h, ans)
            ax.plot([nodo["x"], h["x"]], [-nodo["d"] * DY, -h["d"] * DY],
                    color=C_RUTA if ruta else C_GRIS, lw=3.2 if ruta else 1.4,
                    zorder=1)
            xm = (nodo["x"] + h["x"]) / 2
            ym = (-nodo["d"] * DY - h["d"] * DY) / 2
            ax.text(xm, ym + 0.12, "no" if lado == "no" else "sí", fontsize=fs - 1,
                    ha="center", va="bottom", color=C_RUTA if ruta else C_GRIS,
                    fontweight="bold" if ruta else "normal",
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"), zorder=2)
            rec(h)

    rec(raiz)

    def nodos(nodo):
        ruta = en_ruta(nodo, ans)
        if nodo["leaf"]:
            ax.text(nodo["x"], -nodo["d"] * DY, f"resp.\n{nodo['ans']}", ha="center", va="center",
                    fontsize=fs, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.35", fc=C_HOJA,
                              ec=C_RUTA if ruta else C_BORDE, lw=3 if ruta else 1.2), zorder=3)
        else:
            ax.text(nodo["x"], -nodo["d"] * DY, f"A[{nodo['m']}] < x ?", ha="center", va="center",
                    fontsize=fs,
                    bbox=dict(boxstyle="round,pad=0.4", fc=C_INT,
                              ec=C_RUTA if ruta else C_BORDE, lw=3 if ruta else 1.2), zorder=3)
            nodos(nodo["no"])
            nodos(nodo["si"])

    nodos(raiz)


def hojas(nodo):
    return 1 if nodo["leaf"] else hojas(nodo["no"]) + hojas(nodo["si"])


# ---------------------------------------------------------------
# Figura 3: árboles de decisión (n = 3 y n = 10)
# ---------------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(17, 6.6), gridspec_kw={"width_ratios": [4, 11]})

casos = [(3, None, "n = 3  →  n+1 = 4 hojas, altura h = 2 = ⌈log₂ 4⌉"),
         (10, 5, "n = 10  →  n+1 = 11 hojas, altura h = 4 = ⌈log₂ 11⌉\n(camino de x = 23 resaltado: devuelve 5 con 3 comparaciones)")]

for ax, (n, ans, titulo) in zip(axs, casos):
    raiz = construir(0, n)
    posiciones(raiz, [0])
    h = altura(raiz)
    assert hojas(raiz) == n + 1
    assert h == math.ceil(math.log2(n + 1))     # la cota se alcanza exactamente
    dibujar_arbol(ax, raiz, ans)
    ax.set_title(titulo, fontsize=13, fontweight="bold")
    ax.set_xlim(-0.8, n + 0.8)
    ax.set_ylim(-h * 1.5 - 0.9, 0.9)
    ax.axis("off")

fig.suptitle("Árbol de decisión de la búsqueda binaria: cada comparación tiene 2 salidas, cada hoja es una respuesta 0..n",
             fontsize=14, fontweight="bold")
fig.legend(handles=[Patch(fc=C_INT, ec=C_BORDE, label="nodo interno = una comparación A[m] vs x"),
                    Patch(fc=C_HOJA, ec=C_BORDE, label="hoja = respuesta (primer índice con A[i] ≥ x)")],
           loc="lower center", ncol=2, frameon=False, fontsize=11)
fig.tight_layout(rect=(0, 0.05, 1, 0.94))
fig.savefig("fig3_arbol_decision.png", dpi=150, facecolor="white")
plt.close(fig)


# ---------------------------------------------------------------
# Figura 4: la cota de información
# ---------------------------------------------------------------
def peor_caso(n):
    A = list(range(0, 2 * n, 2))        # valores distintos
    peor = 0
    for x in range(-1, 2 * n + 1):
        lo, hi, it = 0, n, 0
        while lo < hi:
            m = lo + (hi - lo) // 2
            if A[m] < x:
                lo = m + 1
            else:
                hi = m
            it += 1
        peor = max(peor, it)
    return peor


ns = list(range(1, 65))
medido = [peor_caso(n) for n in ns]
cota = [math.ceil(math.log2(n + 1)) for n in ns]
assert medido == cota                    # búsqueda binaria = cota inferior, para todo n probado

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.6), gridspec_kw={"width_ratios": [5, 6]})

# Panel izquierdo: hojas necesarias vs capacidad 2^h  (ejemplo n = 10)
n0 = 10
hs = list(range(0, 6))
cap = [2 ** h for h in hs]
colores = [C_RUTA if c >= n0 + 1 and (h == 0 or 2 ** (h - 1) < n0 + 1) else (C_INT if c >= n0 + 1 else "#cfd8dc")
           for h, c in zip(hs, cap)]
ax1.bar(hs, cap, color=colores, edgecolor=C_BORDE)
for h, c in zip(hs, cap):
    ax1.text(h, c + 0.6, str(c), ha="center", fontsize=11)
ax1.axhline(n0 + 1, color="#1b5e20", ls="--", lw=2)
ax1.text(-0.4, n0 + 1.9, f"n + 1 = {n0 + 1} respuestas posibles", color="#1b5e20", fontsize=11, fontweight="bold")
ax1.set_xlabel("altura h del árbol (nº de comparaciones en el peor caso)", fontsize=11)
ax1.set_ylabel("hojas posibles: 2^h", fontsize=11)
ax1.set_xticks(hs)
ax1.set_title(f"Con h ≤ 3 no caben {n0 + 1} hojas (2³ = 8);\nel menor h con 2^h ≥ {n0 + 1} es h = 4", fontsize=12, fontweight="bold")
ax1.spines[["top", "right"]].set_visible(False)
ax1.set_ylim(0, 38)

# Panel derecho: peor caso medido vs cota inferior
xs = [n / 10 for n in range(10, 650)]
ax2.plot([n for n in xs], [math.log2(n + 1) for n in xs], ls="--", color=C_GRIS, lw=1.8,
         label="log₂(n+1)  (bits de información necesarios)")
ax2.step(ns, cota, where="post", color=C_RUTA, lw=2.6, label="cota inferior ⌈log₂(n+1)⌉ (cualquier algoritmo)")
ax2.plot(ns, medido, "o", ms=5.5, color="#1565c0", mfc="white", mew=1.8,
         label="peor caso medido de la búsqueda binaria")
ax2.set_xlabel("n (tamaño del arreglo)", fontsize=11)
ax2.set_ylabel("comparaciones en el peor caso", fontsize=11)
ax2.set_title("La búsqueda binaria toca la cota inferior en todo n (1 ≤ n ≤ 64)", fontsize=12, fontweight="bold")
ax2.legend(loc="lower right", fontsize=10, frameon=False)
ax2.grid(alpha=0.25)
ax2.spines[["top", "right"]].set_visible(False)
ax2.set_xlim(0, 65)
ax2.set_ylim(0, 7.5)

fig.suptitle("Cota de información: n+1 respuestas ⇒ al menos ⌈log₂(n+1)⌉ comparaciones de 1 bit", fontsize=14, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig("fig4_cota_informacion.png", dpi=150, facecolor="white")
plt.close(fig)
print("ok")
