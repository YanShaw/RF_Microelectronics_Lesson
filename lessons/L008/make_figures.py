"""L008 deterministic figures and independent numerical checks; no noise simulation."""
from pathlib import Path
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle

OUT = Path(__file__).resolve().parent
plt.rcParams.update({'font.size': 11, 'svg.fonttype': 'none'})

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), layout='constrained')
for ax, xs, ys, title in [
    (axes[0], [0, 100, 100, 160], [4, 4, 0, 0], 'One-sided output PSD'),
    (axes[1], [-160, -100, -100, 100, 100, 160], [0, 0, 2, 2, 0, 0], 'Two-sided output PSD'),
]:
    ax.plot(xs, ys, color='#176da5', lw=2)
    ax.fill_between(xs, ys, alpha=.18, color='#176da5')
    ax.set(xlabel='Frequency (kHz)', ylabel=r'PSD ($10^{-18}$ V$^2$/Hz)',
           title=title, ylim=(0, 5))
    ax.grid(alpha=.2)
    ax.text(.5, .9, r'Area = $4\times10^{-13}$ V$^2$', transform=ax.transAxes,
            ha='center')
fig.savefig(OUT/'psd_conventions.svg')
fig.savefig(OUT/'psd_conventions.png', dpi=180)
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 4), layout='constrained')
ax.set(xlim=(-.3, 10.3), ylim=(-.5, 4.5), aspect='equal')
ax.axis('off')
def wire(xs, ys):
    ax.plot(xs, ys, color='#25364a', lw=1.8)
def ground(x, y):
    for i, half in enumerate((.22, .14, .06)):
        wire([x-half, x+half], [y-i*.1]*2)
def resistor(x, y, label):
    wire([x, x], [y, y+.7])
    ax.add_patch(Rectangle((x-.16, y+.7), .32, .9, fc='white', ec='#25364a', lw=1.8))
    wire([x, x], [y+1.6, y+2.4])
    ax.text(x+.27, y+1.1, label, va='center')

# Input voltage source and finite gate-bias input resistance.
ax.add_patch(Circle((.5, 1.2), .32, fill=False, ec='#25364a', lw=1.8))
ax.text(.5, 1.31, '+', ha='center', va='center')
ax.text(.5, 1.06, '-', ha='center', va='center')
wire([.5, .5], [0, .88]); ground(.5, 0)
wire([.5, .5, 1], [1.52, 2.4, 2.4])
ax.add_patch(Rectangle((1, 2.24), .9, .32, fc='white', ec='#25364a', lw=1.8))
wire([1.9, 2.7], [2.4, 2.4]); resistor(2.7, 0, r'$R_{in}$'); ground(2.7, 0)
ax.text(1.45, 2.8, r'$R_{sig}$', ha='center')
ax.text(.05, 1.2, r'$v_{sig}$', ha='right')
ax.text(2.7, 2.8, r'$v_g$', ha='center')
ax.plot(2.7, 2.4, 'o', color='#25364a', ms=4)

# Grounded-source MOS small-signal output: dependent current source and shunts.
wire([4.6, 9.4], [2.4, 2.4]); wire([4.6, 9.4], [0, 0]); ground(7, 0)
wire([4.6, 4.6], [0, .65]); wire([4.6, 4.6], [1.75, 2.4])
ax.add_patch(Polygon([(4.6,.65),(4.25,1.2),(4.6,1.75),(4.95,1.2)],
                     fill=False, ec='#25364a', lw=1.8))
ax.annotate('', xy=(4.6,.88), xytext=(4.6,1.52),
            arrowprops={'arrowstyle':'->','color':'#25364a','lw':1.8})
ax.text(3.65, 1.95, r'$g_m v_g$')
for x, label in [(6.1, r'$r_o$'), (7.6, r'$R_D$'), (9.1, r'$R_L$')]:
    resistor(x, 0, label)
ax.text(9.6, 2.4, r'$v_o$', va='center')
ax.text(5.1, 3.45, 'Common-source small-signal model (midband)', ha='center', fontsize=14)
ax.text(5.1, -.45, 'Source and body: AC ground. Supply: AC ground. Gate draws no intrinsic current.',
        ha='center', fontsize=10)
fig.savefig(OUT/'cs_model.svg')
fig.savefig(OUT/'cs_model.png', dpi=180)
plt.close(fig)

parallel = 1/(1/20000 + 1/5000 + 1/10000)
values = {
    'example_A_rms_uV': {str(r): math.sqrt(3**2+4**2+2*r*3*4) for r in (-1,0,1)},
    'example_B_rms_uV': math.sqrt(4e-18*100e3)*1e6,
    'example_B_400kHz_rms_uV': math.sqrt(4e-18*400e3)*1e6,
    'example_B_gain10_rms_uV': 10*math.sqrt(4e-18*100e3)*1e6,
    'homework2_sum_rms_uV': math.sqrt(2**2+5**2+2*.6*2*5),
    'homework2_difference_rms_uV': math.sqrt(2**2+5**2-2*.6*2*5),
    'homework3_max_bandwidth_Hz': (1e-6/2e-9)**2,
    'checkpoint_parallel_ohm': parallel,
    'checkpoint_gate_gain': -.002*parallel,
    'checkpoint_source_gain_10k': -.002*parallel*100e3/110e3,
    'checkpoint_source_gain_100k': -.002*parallel*.5,
    'checkpoint_output_noise_uV': abs(-.002*parallel*100e3/110e3)*math.sqrt(4e-18*100e3)*1e6,
    'checkpoint_changed_output_noise_uV': abs(-.002*parallel*.5)*math.sqrt(4e-18*100e3)*1e6,
    'checkpoint_rho05_rms_uV': math.sqrt(9+16+12),
}
assert math.isclose(values['example_A_rms_uV']['0'], 5)
assert math.isclose(values['checkpoint_parallel_ohm'], 20000/7)
assert math.isclose(4e-18*100e3, 2e-18*200e3)
(OUT/'verification.json').write_text(json.dumps(values, indent=2)+'\n', encoding='utf-8')
print(json.dumps(values, indent=2))
