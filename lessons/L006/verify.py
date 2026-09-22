"""L006: deterministic lumped small-signal models; not transistor simulation.
Run with Python + numpy + matplotlib. Outputs beside this file.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
plt.rcParams.update({'font.size': 11, 'axes.grid': True})
f = np.logspace(4, 10, 2400)  # Hz
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
results = {}
for color, (fp1, beta, label) in zip(['C0','C1','C2'], [(1e6, 1, 'Original'), (1e5, 1, 'Lower first pole'), (1e6, .1, 'beta = 0.1')]):
    fp2, A0 = 20e6, 100
    w1, w2 = 2*np.pi*np.array([fp1, fp2])
    def loop(freq):
        return beta*A0 / ((1+1j*freq/fp1)*(1+1j*freq/fp2))
    lo, hi = 1e3, 1e10
    for _ in range(100):
        mid = (lo+hi)/2
        if abs(loop(mid)) > 1:
            lo = mid
        else:
            hi = mid
    fc = (lo+hi)/2
    pm = 180+np.angle(loop(fc), deg=True)
    wn = np.sqrt((1+beta*A0)*w1*w2)
    zeta = (w1+w2)/(2*wn)
    poles = np.roots([1, w1+w2, (1+beta*A0)*w1*w2])
    # Independently check the analytic magnitude equation and closed-loop poles.
    assert np.isclose((1+(fc/fp1)**2)*(1+(fc/fp2)**2), (beta*A0)**2)
    assert np.all(poles.real < 0)
    overshoot = 100*np.exp(-np.pi*zeta/np.sqrt(1-zeta*zeta))
    t = np.linspace(0, 300e-9, 3000)
    final = A0/(1+beta*A0)
    p, q = poles
    y = final*(1+(q*np.exp(p*t)-p*np.exp(q*t))/(p-q)).real
    assert abs(100*(y.max()/final-1)-overshoot) < .02
    axes[0].semilogx(f/1e6, 20*np.log10(abs(loop(f))), label=label, color=color)
    axes[1].semilogx(f/1e6, np.angle(loop(f), deg=True), color=color)
    axes[1].plot(fc/1e6, pm-180, 'o', color=color)
    axes[2].plot(t*1e9, y/final, label=label, color=color)
    results[label] = dict(fc_MHz=fc/1e6, PM_deg=pm, zeta=zeta,
                          overshoot_percent=overshoot, closed_loop_DC=final)
axes[0].axhline(0, color='k', lw=.8)
axes[0].set(xlabel='Frequency (MHz)', ylabel='Loop gain (dB)', ylim=(-75,45), xlim=(.01,1000))
axes[1].axhline(-180, color='k', lw=.8, ls='--')
axes[1].set(xlabel='Frequency (MHz)', ylabel='Loop phase (degrees)', xlim=(.01,1000))
axes[2].axhline(1, color='k', lw=.8, ls='--')
axes[2].set(xlabel='Time (ns)', ylabel='Step / final value', xlim=(0,300))
axes[0].legend(fontsize=9)
fig.tight_layout()
fig.savefig(OUT/'feedback.png', dpi=170)
plt.close(fig)

# Exact common-source denominator compared to the Miller estimate.
Rs, Ro, gm, Cgs, Cgd, Co = 1e4, 1e4, .002, .5e-12, .1e-12, .2e-12
a1 = Rs*(Cgs+Cgd)+Ro*(Co+Cgd)+gm*Rs*Ro*Cgd
a2 = Rs*Ro*(Cgs*Co+Cgs*Cgd+Cgd*Co)
roots = np.sort(np.abs(np.roots([a2,a1,1])))/(2*np.pi)
results['Miller'] = dict(Cin_pF=(Cgs+21*Cgd)*1e12,
    estimate_MHz=1/(2*np.pi*Rs*(Cgs+21*Cgd))/1e6,
    illustrative_exact_poles_MHz=(roots/1e6).tolist(),
    exercise_MHz=1/(2*np.pi*5e3*(Cgs+11*Cgd))/1e6)

# Draw the exact two-node small-signal model. Source and body are AC ground.
fig, ax = plt.subplots(figsize=(12,4.6))
ax.set(xlim=(-.7,10.6), ylim=(-.7,4.7), aspect='equal')
ax.axis('off')
def wire(xs, ys): ax.plot(xs,ys,color='#182c44',lw=1.8)
def ground(x,y):
    for dy, half in [(0,.22),(-.09,.15),(-.18,.07)]: wire([x-half,x+half],[y+dy,y+dy])
def cap_v(x,top,bottom,label):
    m=(top+bottom)/2
    wire([x,x],[top,m+.12]); wire([x,x],[m-.12,bottom])
    wire([x-.3,x+.3],[m+.12,m+.12]);wire([x-.3,x+.3],[m-.12,m-.12])
    ax.text(x+.38,m,label,va='center')
def res_h(x1,x2,y,label):
    wire([x1,x1+.3],[y,y]);wire([x2-.3,x2],[y,y])
    ax.add_patch(plt.Rectangle((x1+.3,y-.15),x2-x1-.6,.3,fill=False,lw=1.8))
    ax.text((x1+x2)/2,y+.35,label,ha='center')
ax.add_patch(plt.Circle((0,1.5),.4,fill=False,lw=1.8))
ax.text(0,1.5,'+\n−',ha='center',va='center')
ax.text(-.48,1.5,r'$v_{sig}$',ha='right')
wire([0,0],[1.9,3]);wire([0,0],[1.1,0]);ground(0,0)
res_h(0,2.6,3,r'$R_s$')
wire([2.6,4.6],[3,3]);wire([4.85,7],[3,3])
wire([4.6,4.6],[2.65,3.35]);wire([4.85,4.85],[2.65,3.35])
ax.text(4.72,3.6,r'$C_{gd}$',ha='center')
ax.annotate('',xy=(4.1,3.2),xytext=(3.3,3.2),arrowprops=dict(arrowstyle='->'))
ax.text(3.7,3.5,r'$i_{gd}$',ha='center')
cap_v(2.6,3,0,r'$C_{gs}$');ground(2.6,0)
wire([7,10],[3,3]);cap_v(9.8,3,0,r'$C_o$');ground(9.8,0)
wire([6.2,6.2],[3,1.95]);wire([6.2,6.2],[1.05,0]);ground(6.2,0)
wire([6.2,6.58,6.2,5.82,6.2],[1.95,1.5,1.05,1.5,1.95])
ax.annotate('',xy=(6.2,1.2),xytext=(6.2,1.8),arrowprops=dict(arrowstyle='->'))
ax.text(5.6,1.5,r'$g_m v_g$',ha='right',va='center')
wire([8,8],[3,2]);wire([8,8],[1,0]);ground(8,0)
ax.add_patch(plt.Rectangle((7.83,1),.34,1,fill=False,lw=1.8))
ax.text(8.3,1.5,r'$R_o$',va='center')
for x,label in [(2.6,r'$v_g$'),(7,r'$v_o$')]:
    ax.plot(x,3,'o',color='#182c44',ms=5);ax.text(x,3.8,label,ha='center')
ax.text(5,4.45,'Common-source small-signal model (all grounds are AC ground)',ha='center')
fig.tight_layout()
fig.savefig(OUT/'circuit.png',dpi=180)
fig.savefig(OUT/'circuit.svg')
plt.close(fig)
(OUT/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
