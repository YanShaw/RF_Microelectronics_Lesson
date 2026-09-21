"""Draw the stated AC models and check their KCL; not transistor simulation."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).parent
fig, axs = plt.subplots(1, 3, figsize=(13, 5))
def wire(ax, xs, ys):
    ax.plot(xs, ys, color='#22364b', lw=1.7)
def ground(ax, x, y):
    wire(ax, [x,x], [y,y-.12])
    for k in range(3):
        w=.18-.05*k
        wire(ax,[x-w,x+w],[y-.12-.07*k]*2)
def resistor(ax, x, top, bottom, label):
    mid=(top+bottom)/2
    wire(ax,[x,x],[top,mid+.32]); wire(ax,[x,x],[mid-.32,bottom])
    ax.add_patch(plt.Rectangle((x-.12,mid-.32),.24,.64,fill=False,edgecolor='#22364b',lw=1.7))
    ax.text(x+.19,mid,label,va='center',fontsize=12)
for ax, title in zip(axs, ['Common source (CS)','Common gate (CG)','Source follower (SF)']):
    ax.set(xlim=(-.7,3.8),ylim=(-.75,4.5)); ax.axis('off'); ax.set_title(title,fontsize=15,pad=12)
    # Drain and source rails, and a D-to-S dependent current source.
    wire(ax,[.4,2],[3.3,3.3]); wire(ax,[.4,2],[.7,.7])
    wire(ax,[.4,.4],[3.3,2.4]); wire(ax,[.4,.4],[1.6,.7])
    wire(ax,[.4,.05,.4,.75,.4],[2.4,2,1.6,2,2.4])
    ax.annotate('',xy=(.4,1.77),xytext=(.4,2.23),arrowprops=dict(arrowstyle='->',color='#22364b',lw=1.5))
    ax.text(-.55,2.6,r'$i_c$',fontsize=13)
    resistor(ax,2,3.3,.7,r'$r_o$')
    ax.text(1.1,3.47,'D',fontsize=12); ax.text(1.1,.37,'S',fontsize=12)
    for y in [3.3,.7]: ax.plot(2,y,'o',color='#22364b',ms=4)
ax=axs[0]
ground(ax,.7,.7); wire(ax,[2,3],[3.3,3.3]); resistor(ax,3,3.3,.7,r'$R_L$'); ground(ax,3,.7)
ax.text(2.2,3.65,r'$v_o$',fontsize=13); ax.text(-.5,4.05,r'G: $v_i$; B: AC ground',fontsize=12)
ax.text(-.5,-.65,r'$i_c=g_m v_i$',fontsize=13)
ax=axs[1]
wire(ax,[2,3],[3.3,3.3]); resistor(ax,3,3.3,.7,r'$R_L$'); ground(ax,3,.7)
wire(ax,[-.45,.4],[.7,.7]); ax.text(-.6,.95,r'$v_i$',fontsize=13); ax.text(2.2,3.65,r'$v_o$',fontsize=13)
ax.text(-.5,4.05,'G, B: AC ground',fontsize=12); ax.text(-.5,-.65,r'$i_c=-(g_m+g_{mb})v_i$',fontsize=13)
ax=axs[2]
wire(ax,[2,2.7],[3.3,3.3]); ground(ax,2.7,3.3)
wire(ax,[2,3],[.7,.7]); resistor(ax,3,.7,-.2,r'$R_L$'); ground(ax,3,-.2)
ax.text(2.15,.92,r'$v_o$',fontsize=13); ax.text(-.5,4.05,r'G: $v_i$; B: AC ground',fontsize=12)
ax.text(-.5,-.65,r'$i_c=g_m v_i-(g_m+g_{mb})v_o$',fontsize=12)
fig.suptitle('Small-signal models: bias current sources are open; all ground symbols are AC ground',fontsize=12)
fig.tight_layout(rect=(0,0,1,.94))
fig.savefig(OUT/'three_stages.svg'); fig.savefig(OUT/'three_stages.png',dpi=180)

gm=.01
for gmb in [0,.002]:
    for ro in [20000.,1e12]:
        go=1/ro; g=gm+gmb
        for rl in [500.,1000.,2000.]:
            for rs in [50.,10000.]:
                # CG: unknown D,S; 1 V Thevenin input used only for normalization.
                m=np.array([[1/rl+go,-g-go],[-go,g+go+1/rs]])
                vd,vs=np.linalg.solve(m,[0,1/rs])
                rin=(ro+rl)/(1+g*ro)
                av=(g+go)/(1/rl+go)
                assert np.isclose(vd,av*rin/(rs+rin))
                assert np.isclose(vs/( (1-vs)/rs),rin)
                # Remove load, zero source, inject 1 A into drain.
                mt=np.array([[go,-g-go],[-go,g+go+1/rs]])
                vt,st=np.linalg.solve(mt,[1,0])
                assert np.isclose(vt,ro+(1+g*ro)*rs)
            sf=gm/(g+go+1/rl)
            assert np.isclose(sf/rl+go*sf,gm-g*sf)
for rs in [50.,10000.]:
    for gmb in [0,.002]:
        g=gm+gmb
        print('Example B',rs,gmb,'CG',g*1000/(1+g*rs),'SF',gm/(g+.001))
print('Exercise calculation:',-.005*2000,.005*2000,.005/(.005+1/2000))
assert 1/1.2 < .9
assert np.isclose(.009/(.009+.001),.9)
print('Exercise analysis: body-effect ceiling',1/1.2,'; no-body gm_min = 9 mS')
print('KCL and resistance checks passed.')
