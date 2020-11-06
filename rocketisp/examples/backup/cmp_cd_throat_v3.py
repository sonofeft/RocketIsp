import matplotlib.pyplot as plt
import numpy as np
from rocketisp.nozzle.cd_throat import get_Cd
from calc_full_Cd import calc_Cd
from rocketcea.cea_obj import CEA_Obj

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
colorL = [c for c in colors]

RupArr = np.linspace(0.75, 3, 50)
cd_simpL = [ get_Cd( Rup=Rup, gamma=1.2 ) for Rup in RupArr ]

rangeD = {} # index=pvar, value=list of pvar values
rangeD['Pc'] = reversed([100, 200, 500, 1000, 3000])
rangeD['RWTD'] = [.5, 1, 1.5, 2]
rangeD['gammaInit'] = reversed([1.1, 1.2, 1.3])
rangeD['TcCham'] = [4000, 5000, 6000, 7000]
rangeD['MolWt'] = [15, 20, 25, 30]
rangeD['eps'] = [5, 20, 50, 100, 400]
rangeD['Rthrt'] = reversed([.25, .5, 1, 2, 5, 10])
rangeD['pcentBell'] = reversed([60, 70, 80, 90, 100])
rangeD['THETAI'] = reversed([20, 30, 40])
rangeD['RI'] = reversed([0.5, 1, 3])
rangeD['CR'] = reversed([1.5, 2.5, 4])
rangeD['Best'] = [1]

def make_new_chart( pvar='Pc', Pc=500, Rthrt=1, RWTD=1 ):

    fig, ax = plt.subplots()
    ax.plot(RupArr, cd_simpL,'-k', label='Simple Model' )
    
    inpD = {'Pc':Pc, 'eps':20, 'Rthrt':Rthrt, 'pcentBell':80,
            'THETAI':30.0, 'RWTU':1.0, 'RWTD':RWTD, 'CR':2.5, 'RI':1.0,
            'TcCham':5500.0, 'MolWt':20.0, 'gammaInit':1.2}

    for i, pval in enumerate( rangeD[pvar] ):    
        cd_mlpL = []
        if not pvar=='Best':
            inpD[pvar] = pval
        for Rup in RupArr:
            inpD['RWTU'] = Rup
            cd_mlpL.append( calc_Cd(**inpD) )

        ax.plot(RupArr, cd_mlpL,'-', color=colorL[i],  label='%s=%g'%(pvar, pval) )

    plt.legend()
    plt.title('Cd Throat %s Parametrics'%pvar)
    plt.ylabel('Cd')
    plt.xlabel('Upstream Radius Ratio (RupThroat)')

make_new_chart( pvar='Pc' )
make_new_chart( pvar='RWTD' )
#make_new_chart( pvar='gammaInit' )
#make_new_chart( pvar='TcCham' )
#make_new_chart( pvar='MolWt' )
#make_new_chart( pvar='eps' )
make_new_chart( pvar='Rthrt' )
#make_new_chart( pvar='pcentBell' )
#make_new_chart( pvar='THETAI' )
#make_new_chart( pvar='RI' )
#make_new_chart( pvar='CR' )
make_new_chart( pvar='Best', Pc=3000, Rthrt=10, RWTD=0.5 )

# ------------------------ show -----------------------
plt.show()



