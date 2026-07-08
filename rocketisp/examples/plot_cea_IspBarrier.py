import matplotlib.pyplot as plt

from rocketcea.cea_obj import CEA_Obj
oxName='N2O4'
fuelName='N2H4'
ceaObj = CEA_Obj(oxName=oxName, fuelName=fuelName)

MRbarrier = 0.05
Pc=137.0
eps=35.0

mrL = []
isp_odeL = []
isp_odfL = []

while MRbarrier < 1.0:
    # ........... calc ideal performance parameters
    IspODE_b, cstarODE_b, TcODE_b, MWchm_b, gammaChm_b = \
            ceaObj.get_IvacCstrTc_ChmMwGam( Pc=Pc, MR=MRbarrier, eps=eps)
        
    IspODF_b,_,_ = ceaObj.getFrozen_IvacCstrTc( Pc=Pc, MR=MRbarrier,  eps=eps)

    mrL.append( MRbarrier )
    isp_odeL.append( IspODE_b)
    isp_odfL.append( IspODF_b )

    MRbarrier += 0.01


fig, ax = plt.subplots( figsize=(6,5) )

plt.plot(mrL, isp_odeL, label='IspODE', linewidth=3)
plt.plot(mrL, isp_odfL, label='IspODF', linewidth=3)

plt.legend()
plt.grid()
plt.ylabel('Isp CEA (sec)')
plt.xlabel('Mixture Ratio')


title = 'CEA Isp for %s/%s, eps=%s'%( oxName, fuelName, eps )
plt.title( title )
fig.tight_layout()
# plt.savefig( 'HiPAT_NTO_N2H4_IspBarrier_test.png' )
plt.show()
