import matplotlib.pyplot as plt
from rocketisp.nozzle.huzel_data import getHuzelEntranceExitAngles
from rocketisp.nozzle.six_opt_parab import getOptEntranceExitAngles

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
colorL = [c for c in colors]

fig, ax = plt.subplots()

epsL = [float(i) for i in range(5, 51, 1)]

# ======================= ENTRANCE ANGLE =====================
for ipc,pcb in enumerate([60., 70., 80., 90., 100.]):
    entAngHuzelL = []
    entAngSixL = []
    for eps in epsL:
        (entAng, exitAng) = getHuzelEntranceExitAngles(eps=eps, pcBell=pcb)
        entAngHuzelL.append( entAng )
                
        (entAng, exitAng) = getOptEntranceExitAngles(eps=eps, pcentBell=pcb)
        entAngSixL.append( entAng )

    ax.plot(epsL, entAngHuzelL,'-k', linewidth=4, alpha=0.8 )
    ax.plot(epsL, entAngSixL,'.',  linewidth=4, alpha=0.9, color=colorL[ipc], label='%g%% Bell'%pcb )

plt.legend()
#plt.ylim(15, 40)
plt.xlim(0, 50)
plt.title('6-Prop, vs. Huzel Skewed Parabola Entrance Angle')
plt.ylabel('Entrance Angle (deg)')
plt.xlabel('Area Ratio')
plt.text(20,22, 'Huzel = black\n6-Prop = dotted')

plt.savefig( 'six_vs_Huzel_entrance.png' )

# ===================== EXIT ANGLE ============================
fig, ax = plt.subplots()

for ipc,pcb in enumerate([60., 70., 80., 90., 100.]):
    extAngHuzelL = []
    extAngSixL = []
    for eps in epsL:
        (entAng, exitAng) = getHuzelEntranceExitAngles(eps=eps, pcBell=pcb)
        extAngHuzelL.append( exitAng )
        
        (entAng, exitAng) = getOptEntranceExitAngles(eps=eps, pcentBell=pcb)
        extAngSixL.append( exitAng )

    ax.plot(epsL, extAngHuzelL,'-k', linewidth=4, alpha=0.8 )
    ax.plot(epsL, extAngSixL,'.',  linewidth=4, alpha=0.9, color=colorL[ipc], label='%g%% Bell'%pcb )

plt.legend()
#plt.ylim(15, 40)
plt.xlim(0, 50)
plt.title('6-Prop, vs Huzel Skewed Parabola Exit Angle')
plt.ylabel('Exit Angle (deg)')
plt.xlabel('Area Ratio')
plt.text(18,18, 'Huzel = black\n6-Prop = dotted')

plt.savefig( 'six_vs_Huzel_exit.png' )

plt.show()