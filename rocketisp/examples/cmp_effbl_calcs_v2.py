import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

import numpy as np
from rocketisp.efficiency.calc_All_pcentLossBL import calc_pcentLossBL as calc_pcentLossBL_all


from rocketisp.efficiency.calc_full_pcentLossBL import calc_pcentLossBL
from rocketcea.cea_obj import CEA_Obj

oxName='LOX'
fuelName='LH2'
MR=6.0

oxName='N2O4'
fuelName='MMH'
MR=1.6

ceaObj = CEA_Obj(oxName=oxName, fuelName=fuelName)


prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
colorL = [c for c in colors]

rthrtL = [0.25]
while rthrtL[-1] < 10.0:
    rthrtL.append( 1.1*rthrtL[-1] )

rangeD = {} # index=pvar, value=list of pvar values
rangeD['eps'] = [5, 20, 50, 100]
rangeD['Pc'] = list(reversed([100, 200, 500, 1000, 3000]))

unitsD = {'Pc':'psia', 'Rthrt':'in', 'eps':'', 'pcentBell':'', 'TcCham':'degR'}

def make_new_chart( pvar='Pc', Pc=500, eps=10, pcentBell=80.0, TcCham=5500.0 ):

    fig, ax = plt.subplots( figsize=(7,5) )
    
    if pvar=='Pc':
            
        for i,Pc in enumerate(rangeD['Pc']):
            effblL = []
            for Rthrt in rthrtL:
                #effblL.append( eff_bl_NASA( Dt=2*Rthrt, Pc=Pc, eps=eps) )
                pcloss = calc_pcentLossBL_all(ceaObj, Pc=Pc, eps=eps, Rthrt=Rthrt, pcentBell=pcentBell, MR=MR)
                effblL.append( (100-pcloss)/100.0 )
                
            ax.semilogx(rthrtL, effblL,'--', label='MABL Pc=%g'%Pc, linewidth=3, color=colorL[i] )


        for i,Pc in enumerate(rangeD['Pc']):
            effblL = []
            _, _, TcCham, MolWt, gammaInit = ceaObj.get_IvacCstrTc_ChmMwGam( Pc=Pc, MR=MR, eps=eps)
            for Rthrt in rthrtL:
                effbl = (100-calc_pcentLossBL( Pc=Pc, eps=eps, Rthrt=Rthrt, pcentBell=pcentBell, TcCham=TcCham ))/100.0
                effblL.append( effbl )
            ax.semilogx(rthrtL, effblL,'-', label='MLP Pc=%g'%Pc, color=colorL[i] )

        plt.title('%s Impact on BL efficiency\n(area ratio=%g)'%(pvar, eps))
                
    
    elif pvar=='eps':
            
        for i,eps in enumerate(rangeD['eps']):
            effblL = []
            for Rthrt in rthrtL:
                pcloss = calc_pcentLossBL_all(ceaObj, Pc=Pc, eps=eps, Rthrt=Rthrt, pcentBell=pcentBell, MR=MR)
                effblL.append( (100-pcloss)/100.0 )
            ax.semilogx(rthrtL, effblL,'--', label='MABL eps=%g'%eps, linewidth=3, color=colorL[i] )


        for i,eps in enumerate(rangeD['eps']):
            effblL = []
            _, _, TcCham, MolWt, gammaInit = ceaObj.get_IvacCstrTc_ChmMwGam( Pc=Pc, MR=MR, eps=eps)
            for Rthrt in rthrtL:
                effbl = (100-calc_pcentLossBL( Pc=Pc, eps=eps, Rthrt=Rthrt, pcentBell=pcentBell, TcCham=TcCham ))/100.0
                effblL.append( effbl )
            ax.semilogx(rthrtL, effblL,'-', label='MLP eps=%g'%eps, color=colorL[i] )

        plt.title('%s Impact on BL efficiency\n(Pc=%g psia)'%(pvar, Pc))
    
    plt.gca().xaxis.set_major_formatter(StrMethodFormatter('{x:,g}')) # 2 decimal places
    plt.gca().xaxis.set_minor_formatter(StrMethodFormatter('{x:,g}')) # 2 decimal places
    ax.tick_params(axis='x', which='minor', labelsize=8)
    
    plt.ylabel('BL efficiency')
    plt.xlabel('Throat Radius, inch')
    #plt.ylim( (0.975, 1.0) )
    plt.grid( True )
    plt.legend()
    
    fig.tight_layout()
    #plt.savefig( 'cmp_effbl_calcs_%s.png'%pvar.lower(), dpi=300 )
    
    
make_new_chart( pvar='Pc', eps=100 )
make_new_chart( pvar='eps', Pc=100 )

# ------------------------ show -----------------------
plt.show()

