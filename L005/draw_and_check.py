"""L005: reproducible schematics and independent linear KCL checks."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out=Path(__file__).parent
color='#23394f'
def wire(ax,x,y): ax.plot(x,y,color=color,lw=1.7)
def txt(ax,x,y,s): ax.text(x,y,s,fontsize=12,ha='center',va='center')
def ground(ax,x,y):
    wire(ax,[x,x],[y,y-.10])
    for k in range(3):
        w=.16-.045*k
        wire(ax,[x-w,x+w],[y-.10-.06*k]*2)
def resistor(ax,x,top,bottom,label):
    mid=(top+bottom)/2
    wire(ax,[x,x],[top,mid+.25]);wire(ax,[x,x],[mid-.25,bottom])
    ax.add_patch(plt.Rectangle((x-.10,mid-.25),.2,.5,fill=False,edgecolor=color,lw=1.7))
    txt(ax,x+.38,mid,label)
def mos(ax,x,y,label,gate):
    # Simplified three-terminal NMOS; body omitted as stated in lesson.
    wire(ax,[x,x-.20,x-.20,x],[y+.65,y+.65,y-.65,y-.65])
    wire(ax,[x-.36,x-.36],[y-.43,y+.43])
    wire(ax,[x-.85,x-.36],[y,y])
    txt(ax,x-.78,y+.25,gate);txt(ax,x+.26,y,label)
    txt(ax,x+.17,y+.53,'D');txt(ax,x+.17,y-.53,'S')

fig,axs=plt.subplots(1,2,figsize=(11,6))
for ax in axs: ax.axis('off');ax.set(xlim=(-.3,5),ylim=(-.5,6.3))
ax=axs[0];ax.set_title('Resistively loaded NMOS differential pair',fontsize=13)
wire(ax,[1,3.6],[5.8,5.8]);txt(ax,2.3,6.05,r'$V_{DD}$')
for x,label,inp,r in [(1,'M1',r'$v_1$',r'$R_1$'),(3.6,'M2',r'$v_2$',r'$R_2$')]:
    resistor(ax,x,5.8,4.1,r);wire(ax,[x,x],[4.1,3.65]);mos(ax,x,3,label,inp)
    wire(ax,[x,x],[2.35,1.95]);ax.plot(x,4.1,'o',color=color,ms=4)
wire(ax,[1,3.6],[1.95,1.95]);wire(ax,[2.3,2.3],[1.95,1.35])
txt(ax,.62,4.15,r'$v_{o1}$');txt(ax,3.18,4.15,r'$v_{o2}$');txt(ax,2.6,2.18,r'$v_s$')
ax.add_patch(plt.Circle((2.3,1.05),.30,fill=False,edgecolor=color,lw=1.7))
ax.annotate('',xy=(2.3,.83),xytext=(2.3,1.27),arrowprops=dict(arrowstyle='->',color=color))
wire(ax,[2.3,2.3],[.75,.35]);ground(ax,2.3,.35)
txt(ax,3.25,1.05,r'$I_T$; AC: $R_T$')
ax.text(.0,-.36,'Output voltages are small-signal deviations.\nTail source: DC bias; small-signal resistance RT.',fontsize=10)
ax=axs[1];ax.set_title('NMOS cascode: M1 common source, M2 common gate',fontsize=12)
x=2.5;resistor(ax,x,5.8,4.65,r'$R_L$');txt(ax,x,6.05,r'$V_{DD}$')
wire(ax,[x,x],[4.65,4.45]);mos(ax,x,3.8,'M2',r'$V_B$')
wire(ax,[x,x],[3.15,2.65]);txt(ax,2.88,2.9,r'$v_x$')
mos(ax,x,2,'M1',r'$v_i$');wire(ax,[x,x],[1.35,.9]);ground(ax,x,.9)
wire(ax,[x,3.55],[4.55,4.55]);txt(ax,3.8,4.55,r'$v_o$')
ax.text(.2,-.36,'VB and VDD are AC ground.\nBody effect omitted; both transistors in saturation.',fontsize=10)
fig.tight_layout();fig.savefig(out/'circuits.svg');fig.savefig(out/'circuits.png',dpi=170)

fig,axs=plt.subplots(1,2,figsize=(9,5))
for ax,title,vin in zip(axs,['Differential-mode half circuit','Common-mode half circuit'],[r'$+v_{id}/2$',r'$v_{ic}$']):
    ax.axis('off');ax.set(xlim=(0,4),ylim=(-.4,5.2));ax.set_title(title,fontsize=13)
    resistor(ax,2.5,4.65,3.45,r'$R$');wire(ax,[2.5,1.6],[4.65,4.65]);ground(ax,1.6,4.65)
    mos(ax,2.5,2.7,'M1',vin);wire(ax,[2.5,2.9],[3.4,3.4]);txt(ax,3.25,3.4,r'$v_{o1}$')
    wire(ax,[2.5,2.5],[3.45,3.35])
ax=axs[0];wire(ax,[2.5,2.5],[2.05,1.65]);ground(ax,2.5,1.65);txt(ax,2.3,.65,r'$v_s=0$ (virtual AC ground)')
ax=axs[1];resistor(ax,2.5,2.05,.65,r'$2R_T$');ground(ax,2.5,.65)
fig.tight_layout();fig.savefig(out/'half_circuits.svg');fig.savefig(out/'half_circuits.png',dpi=170)

def solve_pair(gm,r1,r2,rt,v1,v2,ro=np.inf):
    go=0 if np.isinf(ro) else 1/ro
    gt=0 if np.isinf(rt) else 1/rt
    # Drain 1, drain 2, and common source KCL.
    a=np.array([[1/r1+go,0,-gm-go],[0,1/r2+go,-gm-go],[-go,-go,2*(gm+go)+gt]])
    b=np.array([-gm*v1,-gm*v2,gm*(v1+v2)])
    ans=np.linalg.solve(a,b)
    assert np.allclose(a@ans,b)
    return ans
gm=.004;r=5000.
for rt in [10000.,20000.,np.inf]:
    d1,d2,vs=solve_pair(gm,r,r,rt,.0005,-.0005)
    assert np.allclose([d1,d2,vs],[-.01,.01,0])
    for ro in [20000.,100000.]:
        d1,d2,vs=solve_pair(gm,r,r,rt,.0005,-.0005,ro)
        assert np.isclose(d1,-gm/(1/r+1/ro)*.0005)
        assert np.isclose(vs,0)
    d1,d2,vs=solve_pair(gm,5050,4950,rt,.01,.01)
    expected=0 if np.isinf(rt) else -gm*100/(1+2*gm*rt)*.01
    assert np.isclose(d1-d2,expected)
    print('CM mismatch',rt,'ohm: output1, output2, difference, source =',d1,d2,d1-d2,vs)
gm1=gm2=.004;ro1=ro2=20000.
go1=1/ro1;go2=1/ro2
# Output-to-source isolation: vo = 1 V, gate inputs zero.
vx=go2/(gm2+go1+go2)
rout=1/(-gm2*vx+go2*(1-vx))
assert np.isclose(rout,ro1+ro2+gm2*ro1*ro2)
assert np.isclose(vx,ro1/rout)
print('Cascode Rout and vx/vo:',rout,vx)
print('Exercise 2 gains:',-.003*8000/2,-.003*8000)
print('Exercise 3 min RT:',(gm*100/.001-1)/(2*gm))
assert np.isclose(gm*100/(1+2*gm*49875),.001)
assert np.isclose(gm*40.25/(1+2*gm*20000),.001)
print('CMRR dB:',20*np.log10(8050))
print('All KCL checks passed; linear model only.')
