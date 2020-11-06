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
rangeD['Rthrt'] = reversed([.25, .5, 1, 2, 10])
rangeD['Best'] = ['high Pc, big Rthrt']
rangeD['Worst'] = ['low Pc, small Rthrt']

unitsD = {'Pc':'psia', 'Rthrt':'in', 'Best':'', 'Worst':''}

def make_new_chart( pvar='Pc', Pc=500, Rthrt=1 ):

    fig, ax = plt.subplots( figsize=(4,4) )
    ax.plot(RupArr, cd_simpL,'--k', label='Simple Model', linewidth=3 )
    
    inpD = {'Pc':Pc,  'Rthrt':Rthrt}

    for i, pval in enumerate( rangeD[pvar] ):    
        cd_mlpL = []
        if pvar in ['Best','Worst']:
            pval_str = pval
        else:
            inpD[pvar] = pval
            pval_str = '%g'%pval
        for Rup in RupArr:
            inpD['RWTU'] = Rup
            cd_mlpL.append( calc_Cd(**inpD) )

        ax.plot(RupArr, cd_mlpL,'-', color=colorL[i],  label='%s=%s %s'%(pvar, pval, unitsD[pvar]) )

    plt.legend()
    if pvar=='Pc':
        plt.title('%s Impact on Cd Throat\n(Rthrt=%g inch)'%(pvar, Rthrt))
    elif pvar=='Rthrt':
        plt.title('%s Impact on Cd Throat\n(Pc=%g psia)'%(pvar, Pc))
    elif pvar in ['Best','Worst']:
        plt.title('Cd Throat\n(Pc=%g psia, Rthrt=%g inch)'%(Pc, Rthrt))
    
    
    plt.ylabel('Cd')
    plt.xlabel('Upstream Radius Ratio (RupThroat)')
    plt.ylim( (0.975, 1.0) )
    plt.grid( True )
    
    fig.tight_layout()
    plt.savefig( 'cmp_cd_calcs_%s.png'%pvar.lower(), dpi=300 )

make_new_chart( pvar='Pc' )
make_new_chart( pvar='Rthrt' )
make_new_chart( pvar='Best', Pc=3000, Rthrt=10 )
make_new_chart( pvar='Worst', Pc=100, Rthrt=.25 )

# ------------------------ show -----------------------
plt.show()



