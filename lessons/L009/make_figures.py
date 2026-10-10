"""Draw the L009 Thevenin source and matched-load reference circuits."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


OUT = Path(__file__).resolve().parent
INK = "#172b3a"
BLUE = "#1769aa"
plt.rcParams.update({"font.size": 12, "svg.fonttype": "none"})
fig, axes = plt.subplots(1, 2, figsize=(13, 5.6), facecolor="white")


def wire(ax, xs, ys):
    ax.plot(xs, ys, color=INK, lw=2, solid_capstyle="round")


for ax, matched in zip(axes, (False, True)):
    ax.set_aspect("equal")
    ax.set_xlim(-0.3, 6.4)
    ax.set_ylim(-1.1, 4.85)
    ax.axis("off")

    # Ideal voltage source: positive upper terminal, negative lower terminal.
    wire(ax, [1, 1], [0.5, 1.5])
    wire(ax, [1, 1, 2.15], [2.5, 3.5, 3.5])
    ax.add_patch(Circle((1, 2), 0.5, fill=False, edgecolor=INK, lw=2))
    ax.text(1, 2.21, "+", ha="center", va="center", color=INK, fontsize=17)
    ax.text(1, 1.79, "−", ha="center", va="center", color=INK, fontsize=17)
    ax.text(0.25, 2, "$v_s(t)$\nAC", ha="right", va="center", color=INK)

    # Thevenin series resistance. Rectangle is the IEC resistor symbol.
    ax.add_patch(Rectangle((2.15, 3.28), 1.4, 0.44,
                           fill=False, edgecolor=INK, lw=2))
    ax.text(2.85, 4.05, "$R_s=50\\,\\Omega$", ha="center", color=INK)
    wire(ax, [3.55, 5], [3.5, 3.5])
    wire(ax, [1, 5], [0.5, 0.5])

    # Both source and load use the same lower reference node.
    wire(ax, [2.85, 2.85], [0.5, 0.15])
    for y, half_width in [(0.15, 0.32), (0.01, 0.22), (-0.13, 0.1)]:
        wire(ax, [2.85 - half_width, 2.85 + half_width], [y, y])
    ax.text(3.3, -0.06, "0 V reference", color=INK, fontsize=10, va="center")

    ax.annotate("", xy=(4.75, 3.86), xytext=(3.85, 3.86),
                arrowprops={"arrowstyle": "->", "color": BLUE, "lw": 1.8})
    ax.text(4.3, 4.06, "$i(t)$" if matched else "$i=0$",
            ha="center", color=BLUE)

    if matched:
        wire(ax, [5, 5], [3.5, 2.65])
        ax.add_patch(Rectangle((4.78, 1.35), 0.44, 1.3,
                               fill=False, edgecolor=INK, lw=2))
        wire(ax, [5, 5], [1.35, 0.5])
        ax.text(4.55, 2, "$R_L$\n$50\\,\\Omega$", ha="right",
                va="center", color=INK)
        title = "(b) Matched load"
        voltage = "$v_L(t)$"
        caption = "$R_L=R_s$  $\\Rightarrow$  $v_L(t)=v_s(t)/2$"
    else:
        title = "(a) Open-circuit reference"
        voltage = "$v_{oc}(t)$"
        caption = "$R_L$ removed:  $v_{oc}(t)=v_s(t)$"

    for y in (0.5, 3.5):
        ax.add_patch(Circle((5, y), 0.07, facecolor="white",
                            edgecolor=INK, lw=1.7, zorder=5))
    ax.text(5.48, 3.35, "+", color=BLUE, ha="center", fontsize=17)
    ax.text(5.48, 0.61, "−", color=BLUE, ha="center", fontsize=17)
    ax.text(5.48, 2, voltage, color=BLUE, ha="center", va="center")
    ax.text(2.9, 4.65, title, ha="center", weight="bold", fontsize=14,
            color=INK)
    ax.text(2.9, -0.7, caption, ha="center", color=INK, fontsize=12)

fig.subplots_adjust(left=0.025, right=0.985, bottom=0.05, top=0.99, wspace=0.06)
for extension in ("svg", "png"):
    fig.savefig(OUT / f"source_load.{extension}", dpi=180, facecolor="white")
plt.close(fig)
print("Saved source_load.svg and source_load.png")
