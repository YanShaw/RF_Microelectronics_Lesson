"""Reproducible L007 teaching figures and numerical cross-checks (not device simulation)."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon

OUT = Path(__file__).resolve().parent
plt.rcParams.update({"font.size": 11, "figure.dpi": 160})

# RC circuit: input voltage source, R in series, C to the common ground.
fig, ax = plt.subplots(figsize=(9, 3.3))
ax.set(xlim=(-0.6, 8.1), ylim=(-0.6, 2.8), aspect="equal")
ax.axis("off")
def wire(xs, ys):
    ax.plot(xs, ys, color="#23344d", lw=2)
wire([0, 0], [0, .65])
wire([0, 0, 2], [1.35, 2, 2])
ax.add_patch(Circle((0, 1), .35, fill=False, lw=2, color="#23344d"))
ax.text(0, 1.12, "+", ha="center", va="center")
ax.text(0, .85, "−", ha="center", va="center")
ax.text(.55, .95, r"$x(t)$", va="center")
ax.add_patch(Rectangle((2, 1.8), 1.2, .4, fill=False, lw=2, color="#23344d"))
ax.text(2.6, 2.35, r"$R$", ha="center")
wire([3.2, 5, 7], [2, 2, 2])
ax.plot(5, 2, "o", color="#23344d", ms=5)
wire([5, 5], [2, 1.15])
wire([4.55, 5.45], [1.15, 1.15])
wire([4.55, 5.45], [.9, .9])
wire([5, 5, 0], [.9, 0, 0])
ax.text(5.6, 1.02, r"$C$", va="center")
ax.annotate("", xy=(4.55, 2), xytext=(3.5, 2), arrowprops={"arrowstyle": "->", "lw": 2, "color": "#bd5b23"})
ax.text(4, 2.28, r"$i_R$", ha="center", color="#bd5b23")
ax.annotate("", xy=(4.1, .65), xytext=(4.1, 1.45), arrowprops={"arrowstyle": "->", "lw": 2, "color": "#bd5b23"})
ax.text(3.65, 1.03, r"$i_C$", ha="center", color="#bd5b23")
ax.text(7, 1.75, "+", ha="center")
ax.text(7, 1.08, r"$y(t)$", ha="center")
ax.text(7, .4, "−", ha="center")
wire([2.5, 2.5], [0, -.18])
for width, yy in [(.7, -.18), (.45, -.3), (.2, -.42)]:
    wire([2.5-width/2, 2.5+width/2], [yy, yy])
ax.text(3.1, -.35, "common ground; output unloaded", fontsize=10)
fig.tight_layout()
for ext in ("png", "svg"):
    fig.savefig(OUT / f"rc_filter.{ext}", bbox_inches="tight")
plt.close(fig)

# Arrows represent Fourier delta weights in mV, not finite PSD peaks.
fig, axes = plt.subplots(3, 1, figsize=(10, 7.4), sharex=True)
rows = [([-101, 101], [5, 5], "Input: 10 mV peak at 101 MHz"),
        ([-201, -1, 1, 201], [2.5]*4, "Multiply by cos(2π · 100 MHz · t)"),
        ([-1, 1], [2.5, 2.5], "Ideal LPF: |f| < 2 MHz")]
for ax, (freqs, weights, title) in zip(axes, rows):
    ax.axhline(0, color="#6b7280", lw=.8)
    for freq, weight in zip(freqs, weights):
        ax.annotate("", xy=(freq, weight), xytext=(freq, 0), arrowprops={"arrowstyle": "->", "lw": 1.8, "color": "#196d98"})
        # Place near-zero labels apart, keeping the actual arrows at ±1 MHz.
        if abs(freq) == 1:
            ax.annotate(f"{freq:+d}: {weight:g}", xy=(freq, weight),
                        xytext=(freq*35, weight+.65), ha="right" if freq < 0 else "left",
                        fontsize=10, arrowprops={"arrowstyle": "-", "lw": .7})
        else:
            ax.text(freq, weight+.2, f"{freq:+d}: {weight:g}", ha="center", fontsize=10)
    ax.set_title(title, loc="left", fontsize=12)
    ax.set(ylabel="Delta weight (mV)", ylim=(-.15, 6.1), xlim=(-230, 230))
    ax.grid(axis="x", alpha=.15)
axes[-1].set_xlabel("Frequency f (MHz); arrows at ±1 MHz are close on this scale")
axes[-1].set_xticks([-201, -101, 0, 101, 201])
fig.tight_layout(h_pad=1.2)
for ext in ("png", "svg"):
    fig.savefig(OUT / f"mixing_lines.{ext}", bbox_inches="tight")
plt.close(fig)

# A triangular real even M(f) is chosen only to make translations visible.
fig, axes = plt.subplots(3, 1, figsize=(10, 7), sharex=True)
def band(ax, center, height, color):
    ax.add_patch(Polygon([(center-2, 0), (center, height), (center+2, 0)],
                         facecolor=color, edgecolor=color, alpha=.75))
for ax, title in zip(axes, ["Baseband M(f): B = 2 (illustrative units)",
                          "x(t) = m(t) cos(2πfc t): fc = 20; each copy × 1/2",
                          "Multiply by cos(2πfLO t): fLO = 15; each copy × 1/4"]):
    ax.set_title(title, loc="left", fontsize=11)
    ax.axhline(0, color="#6b7280", lw=.8)
    ax.set(ylim=(-.03, 1.3), xlim=(-40, 40), ylabel="Relative spectrum")
    ax.grid(alpha=.15)
band(axes[0], 0, 1, "#417856")
for center in (-20, 20):
    band(axes[1], center, .5, "#196d98")
for center in (-35, -5, 5, 35):
    band(axes[2], center, .25, "#bd5b23")
axes[-1].set_xlabel("Frequency f (same arbitrary unit throughout); bandwidth unchanged")
axes[-1].set_xticks([-35, -20, -5, 0, 5, 20, 35])
fig.tight_layout(h_pad=1.3)
for ext in ("png", "svg"):
    fig.savefig(OUT / f"band_translation.{ext}", bbox_inches="tight")
plt.close(fig)

# Independent time-domain product and Fourier-coefficient checks.
fs, n = 1e9, 10000
t = np.arange(n) / fs
x = .010 * np.cos(2*np.pi*101e6*t)
y = x * np.cos(2*np.pi*100e6*t)
expected = .005 * (np.cos(2*np.pi*1e6*t) + np.cos(2*np.pi*201e6*t))
err = float(np.max(np.abs(y-expected)))
coeff = np.fft.fft(y) / n
delta_f = fs / n
weights = {str(int(f)): float(abs(coeff[int(round(f/delta_f)) % n]))
           for f in (-201e6, -1e6, 1e6, 201e6)}
assert err < 1e-12
assert all(abs(w-.0025) < 1e-12 for w in weights.values())
assert np.max(np.abs(2*y - 2*expected)) < 1e-12
phasor_sum = .002*np.exp(1j*np.pi/3) + .002*np.exp(-1j*np.pi/3)
assert abs(phasor_sum-.002) < 1e-15
R, C = 1000., 1/(2*np.pi*1e6*1000.)
H = 1/(1+1j*2*np.pi*1e6*R*C)
assert abs(abs(H)-1/np.sqrt(2)) < 1e-15
report = {
    "model": "deterministic ideal voltage multiplication; no transistor model",
    "sample_rate_Hz": fs, "samples": n, "bin_spacing_Hz": delta_f,
    "window": "rectangular; coherent integer cycles", "normalization": "FFT/N, two-sided complex coefficients",
    "max_product_identity_error_V": err, "two_sided_weights_V": weights,
    "RC_at_fc_magnitude": float(abs(H)), "RC_at_fc_phase_deg": float(np.angle(H, deg=True)),
    "phasor_sum_peak_V": float(phasor_sum.real),
    "example_A_each_tone_peak_V": .005, "example_A_each_tone_rms_V": .005/np.sqrt(2),
    "example_B_cos_IF_peak_V": .005, "example_B_2cos_IF_peak_V": .010,
    "exercise_2_each_tone_peak_V": .006, "exercise_2_each_delta_weight_V": .003,
    "exercise_3_new_IF_Hz": 3e6, "exercise_3_new_sum_Hz": 199e6,
}
(OUT / "verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
