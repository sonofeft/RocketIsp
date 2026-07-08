import matplotlib.pyplot as plt
import numpy as np
from rocketisp.geometry import Geometry
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream
from rocketisp.rocket_isp import RocketThruster

# create CoreStream with area ratio=375:1, Pc=137, FFC=30% and effERE=0.99
C = CoreStream( geomObj=Geometry(eps=375), 
                effObj=Efficiencies(ERE=0.99), pcentFFC=30,
                oxName='N2O4', fuelName='N2H4',  MRcore=1.2,
                Pc=137, Pamb=0)

# instantiate RocketThruster
R = RocketThruster(name='100 lbf Aerojet HiPAT R-4D', coreObj=C)

ispodeL  = [] # list of IspODE  (one-dimensional equilibrium)
ispodkL  = [] # list of IspODK  (one-dimensional kinetic)
ispdelL  = [] # list of IspDel  (delivered Isp)
mrnetL   = [] # list of MRthruster (net mixture ratio of core and barrier)
mrcoreL  = [] # list of MRcore  (core stream tube mixture ratio)

mrbarrL = [] # list of MRbarrier
mrwallL = [] # list of MRwall
twallgL = [] # list of Twallgas
ispodebarrL = [] # list of IspODE_b

ispodfbarrL = [] # list of IspODF_b
ispodkbarrL = [] # list of IspODK_b
effnozbarrL = [] # list of effNoz_b
efferebarrL = [] # list of effERE_b
effispbarrL = [] # list of effIsp_b
effkinbarrL = [] # list of effKin_b
#  = [] # list of 

for MRcore in np.linspace( 0.9, 1.9, num=60 ):
    C.reset_attr( 'MRcore', MRcore )
    R.scale_Rt_to_Thrust( 100 , Pamb=0.0 )

    B = C.barrierObj

    ispodeL.append( C('IspODE') )
    ispodkL.append( C('IspODK') )
    ispdelL.append( C('IspDel') )
    mrnetL.append( C('MRthruster') )
    mrcoreL.append( C('MRcore') )

    mrbarrL.append( B('MRbarrier') )
    mrwallL.append( B('MRwall') )
    twallgL.append( B('Twallgas') )
    ispodebarrL.append( B('IspODE_b') )

    ispodfbarrL.append( B('IspODF_b') )
    ispodkbarrL.append( B('IspODK_b') )
    effnozbarrL.append( B('effNoz_b') )
    efferebarrL.append( B('effERE_b') )
    effispbarrL.append( B('effIsp_b') )
    effkinbarrL.append( B('effKin_b') )

    
    #print( 'MRcore/MReng=%g/%g'%(MRcore, C('MRthruster')), '   effNoz=%g'%C.effObj('Noz'), '   effDiv=%g'%C.effObj('Div'), '   effBL=%g'%C.effObj('BL') )

fig, ax = plt.subplots( figsize=(6,5) )

plt.plot(mrcoreL, ispodeL, label='IspODE', linewidth=3)
plt.plot(mrcoreL, ispodkL, label='IspODK', linewidth=3)
plt.plot(mrnetL, ispdelL, label='IspDel', linewidth=3)
plt.legend()
plt.grid()
plt.ylabel('Isp (sec)')
plt.xlabel('Mixture Ratio\n(MRcore for IspODE and IspODK, MRengine for IspDel)')

imL = sorted([(i,m, mc) for i,m,mc in zip(ispdelL, mrnetL, mrcoreL)])
subtitle = 'max IspDel=%.1f at MRthruster=%.2f, MRcore=%.2f'%imL[-1]

title = '%s/%s Area Ratio=%g:1 %%Bell=%g %%FFC=%g\n'%( C.oxName, C.fuelName, C.geomObj.eps, 
        C.geomObj.pcentBell, C.barrierObj.pcentFFC ) + subtitle
plt.title( title )
fig.tight_layout()
plt.savefig( 'HiPAT_NTO_N2H4_IspDel.png' )
# plt.show()

# ========================== BARRIER Temperature ================================

fig, ax = plt.subplots( figsize=(6,5) )

plt.plot(mrcoreL, twallgL, label='Twall_gasBarrier', linewidth=3)
# plt.plot(mrcoreL, efferebarrL, label='EffEREBarrier', linewidth=3)
# plt.plot(mrcoreL, effispbarrL, label='EffIspBarrier', linewidth=3)
# plt.plot(mrcoreL, effkinbarrL, label='EffKinBarrier', linewidth=3)

plt.legend()
plt.grid()
plt.ylabel('Temperature (degR)')
plt.xlabel('MRcore)')


title = '%s/%s Area Ratio=%g:1 %%Bell=%g %%FFC=%g\n'%( C.oxName, C.fuelName, C.geomObj.eps, 
        C.geomObj.pcentBell, C.barrierObj.pcentFFC ) + subtitle
plt.title( title )
fig.tight_layout()
plt.savefig( 'HiPAT_NTO_N2H4_TBarrier.png' )

# ========================== BARRIER Efficiency ================================

fig, ax = plt.subplots( figsize=(6,5) )

plt.plot(mrcoreL, effnozbarrL, label='EffNozBarrier', linewidth=3)
plt.plot(mrcoreL, efferebarrL, label='EffEREBarrier', linewidth=3)
plt.plot(mrcoreL, effispbarrL, label='EffIspBarrier', linewidth=3)
plt.plot(mrcoreL, effkinbarrL, label='EffKinBarrier', linewidth=3)

plt.legend()
plt.grid()
plt.ylabel('Efficiency')
plt.xlabel('MRcore)')


title = '%s/%s Area Ratio=%g:1 %%Bell=%g %%FFC=%g\n'%( C.oxName, C.fuelName, C.geomObj.eps, 
        C.geomObj.pcentBell, C.barrierObj.pcentFFC ) + subtitle
plt.title( title )
fig.tight_layout()
plt.savefig( 'HiPAT_NTO_N2H4_EffBarrier.png' )

# ========================== BARRIER Isp ================================

fig, ax = plt.subplots( figsize=(6,5) )

plt.plot(mrcoreL, ispodebarrL, label='IspODEbarr', linewidth=3)
plt.plot(mrcoreL, ispodkbarrL, label='IspODKbarr', linewidth=3)
plt.plot(mrcoreL, ispodfbarrL, label='IspODFbarr', linewidth=3)

plt.legend()
plt.grid()
plt.ylabel('Isp Barrier (sec)')
plt.xlabel('MRcore for IspODE, IspODK and IspODF Barrier)')


title = '%s/%s Area Ratio=%g:1 %%Bell=%g %%FFC=%g\n'%( C.oxName, C.fuelName, C.geomObj.eps, 
        C.geomObj.pcentBell, C.barrierObj.pcentFFC ) + subtitle
plt.title( title )
fig.tight_layout()
plt.savefig( 'HiPAT_NTO_N2H4_IspBarrier.png' )

# ========================== BARRIER MR ================================

fig, ax = plt.subplots( figsize=(6,5) )

plt.plot(mrcoreL, mrcoreL, label='MRcore', linewidth=3)
plt.plot(mrcoreL, mrnetL, label='MRengine', linewidth=3)
plt.plot(mrcoreL, mrbarrL, label='MRbarrier', linewidth=3)
plt.plot(mrcoreL, mrwallL, label='MRgas_at_wall', linewidth=3)

plt.legend()
plt.grid()
plt.ylabel('Mixture Ratio')
plt.xlabel('MRcore')


title = '%s/%s Area Ratio=%g:1 %%Bell=%g %%FFC=%g\n'%( C.oxName, C.fuelName, C.geomObj.eps, 
        C.geomObj.pcentBell, C.barrierObj.pcentFFC ) + subtitle
plt.title( title )
fig.tight_layout()
plt.savefig( 'HiPAT_NTO_N2H4_MRBarrier.png' )

# ======================== printed output ============================
plt.show()
# ...END...
#print( 'max IspDel=%.1f at MRthruster=%.3f, MRcore=%.3f '%imL[-1] )
i,m,mc = imL[-1]
C.reset_attr( 'MRcore', mc )
R.scale_Rt_to_Thrust( 100 , Pamb=0.0 )
R.summ_print()

#C.effObj.summ_print()
