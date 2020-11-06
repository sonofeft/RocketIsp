import matplotlib.pyplot as plt
import numpy as np
from rocketisp.nozzle.cd_throat import get_Cd
from calc_full_Cd import calc_Cd
from rocketcea.cea_obj import CEA_Obj

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
colorL = [c for c in colors]

ceaObj = CEA_Obj(oxName='N2O4', fuelName='MMH')
_, _, TcCham, MolWt, gammaInit = ceaObj.get_IvacCstrTc_ChmMwGam( Pc=500, MR=1.5, eps=20)

RupArr = np.linspace(0.75, 3, 50)

cd_simpL = [ get_Cd( Rup=Rup, gamma=gammaInit ) for Rup in RupArr ]

# ----------- CR -----------------------
fig, ax = plt.subplots()
ax.plot(RupArr, cd_simpL,'-k', label='Simple, gam=%g'%gammaInit )
for CR in [2, 2.5, 3, 4]:
    cd_mlpL = [calc_Cd(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=1.5,
                 THETAI=30.0, RWTU=Rup, RWTD=1.0, CR=CR, RI=1.0)
                 for Rup in RupArr]

    ax.plot(RupArr, cd_mlpL,'--',  label='MLP, CR=%g'%CR )

plt.legend()
#plt.ylim(15, 40)
#plt.xlim(0, 50)
plt.title('Cd Throat')
plt.ylabel('Cd')
plt.xlabel('Upstream Radius Ratio (Rup)')


# ----------- THETAI -----------------------
fig, ax = plt.subplots()
ax.plot(RupArr, cd_simpL,'-k', label='Simple, gam=%g'%gammaInit )
for THETAI in [20, 25, 30, 35]:
    cd_mlpL = [calc_Cd(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=1.5,
                 THETAI=THETAI, RWTU=Rup, RWTD=1.0, CR=2.5, RI=1.0)
                 for Rup in RupArr]

    ax.plot(RupArr, cd_mlpL,'--',  label='MLP, THETAI=%g'%THETAI )

plt.legend()
#plt.ylim(15, 40)
#plt.xlim(0, 50)
plt.title('Cd Throat')
plt.ylabel('Cd')
plt.xlabel('Upstream Radius Ratio (Rup)')

# ----------- MR -----------------------
fig, ax = plt.subplots()
ax.plot(RupArr, cd_simpL,'-k', label='Simple, gam=%g'%gammaInit )

for MR in [1, 1.4, 1.8, 2.2, 2.4]:
    cd_mlpL = [calc_Cd(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=MR,
                 THETAI=30.0, RWTU=Rup, RWTD=1.0, CR=2.5, RI=1.0)
                 for Rup in RupArr]

    ax.plot(RupArr, cd_mlpL,'--',  label='MLP, MR=%g'%MR )

plt.legend()
#plt.ylim(15, 40)
#plt.xlim(0, 50)
plt.title('Cd Throat')
plt.ylabel('Cd')
plt.xlabel('Upstream Radius Ratio (Rup)')

# ----------- RWTD -----------------------
fig, ax = plt.subplots()
ax.plot(RupArr, cd_simpL,'-k', label='Simple, gam=%g'%gammaInit )

for RWTD in [0.5, 1, 1.5, 2]:
    cd_mlpL = [calc_Cd(ceaObj, Pc=500, eps=20, Rthrt=1, pcentBell=80, MR=1.5,
                 THETAI=30.0, RWTU=Rup, RWTD=RWTD, CR=2.5, RI=1.0)
                 for Rup in RupArr]

    ax.plot(RupArr, cd_mlpL,'--',  label='MLP, RWTD=%g'%RWTD )

plt.legend()
#plt.ylim(15, 40)
#plt.xlim(0, 50)
plt.title('Cd Throat')
plt.ylabel('Cd')
plt.xlabel('Upstream Radius Ratio (Rup)')


# ----------- Pc -----------------------
fig, ax = plt.subplots()
ax.plot(RupArr, cd_simpL,'-k', label='Simple, gam=%g'%gammaInit )

for Pc in [100, 200, 500, 1000]:
    cd_mlpL = [calc_Cd(ceaObj, Pc=Pc, eps=20, Rthrt=1, pcentBell=80, MR=1.5,
                 THETAI=30.0, RWTU=Rup, RWTD=1.0, CR=2.5, RI=1.0)
                 for Rup in RupArr]

    ax.plot(RupArr, cd_mlpL,'--',  label='MLP, Pc=%g'%Pc )

plt.legend()
#plt.ylim(15, 40)
#plt.xlim(0, 50)
plt.title('Cd Throat')
plt.ylabel('Cd')
plt.xlabel('Upstream Radius Ratio (Rup)')

# ----------- Rthrt -----------------------
fig, ax = plt.subplots()
ax.plot(RupArr, cd_simpL,'-k', label='Simple, gam=%g'%gammaInit )

for Rthrt in [5.0, 1.0, 0.2]:
    cd_mlpL = [calc_Cd(ceaObj, Pc=200, eps=20, Rthrt=Rthrt, pcentBell=80, MR=1.5,
                 THETAI=30.0, RWTU=Rup, RWTD=1.0, CR=2.5, RI=1.0)
                 for Rup in RupArr]

    ax.plot(RupArr, cd_mlpL,'--',  label='MLP, Rthrt=%g'%Rthrt )

plt.legend()
#plt.ylim(15, 40)
#plt.xlim(0, 50)
plt.title('Cd Throat')
plt.ylabel('Cd')
plt.xlabel('Upstream Radius Ratio (Rup)')



# ------------------------ show -----------------------
plt.show()

