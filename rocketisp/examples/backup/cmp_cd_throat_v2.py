import matplotlib.pyplot as plt
import numpy as np
from rocketisp.nozzle.cd_throat import get_Cd
from calc_full_Cd import calc_Cd
from rocketcea.cea_obj import CEA_Obj

RupArr = np.linspace(0.75, 3, 50)
cd_simpL = [ get_Cd( Rup=Rup, gamma=1.2 ) for Rup in RupArr ]

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
colorL = [c for c in colors]

# ----------- Pc -----------------------
fig, ax = plt.subplots()
ax.plot(RupArr, cd_simpL,'-k', label='Simple, gam=%g'%1.2 )

for oxName, fuelName, MR, line_style in [('N2O4','A50', 1.6, '-'), ('LOX','LH2', 6, '--')]:
    ceaObj = CEA_Obj(oxName=oxName, fuelName=fuelName)
    
    for i,Pc in enumerate([3000, 500, 100]):
        _, _, TcCham, MolWt, gammaInit = ceaObj.get_IvacCstrTc_ChmMwGam( Pc=Pc, MR=MR, eps=20)
        cd_mlpL = [calc_Cd( Pc=Pc, eps=20, Rthrt=1, pcentBell=80,
                     THETAI=30.0, RWTU=Rup, RWTD=1.0, CR=2.5, RI=1.0,
                     TcCham=TcCham, MolWt=MolWt, gammaInit=gammaInit)
                     for Rup in RupArr]

        ax.plot(RupArr, cd_mlpL,line_style, color=colorL[i],  label='%s/%s, Pc=%g'%(oxName, fuelName, Pc) )

plt.legend()
plt.title('Cd Throat')
plt.ylabel('Cd')
plt.xlabel('Upstream Radius Ratio (RupThroat)')


# ------------------------ show -----------------------
plt.show()


