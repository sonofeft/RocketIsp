"""
plot perfect injector Isp vs MR
"""
import matplotlib.pyplot as plt
import pylab
prop_cycle = pylab.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
COLORL = [c for c in colors]

from rocketcea.biprop_utils.InterpProp_scipy import InterpProp
from rocketcea.biprop_utils.goldSearch import search_max as gold_search_max
from rocketcea.biprop_utils.mr_t_limits import MR_Temperature_Limits
from rocketcea.biprop_utils.mr_peak_at_eps_pc import MR_Peak_At_EpsPc

from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
from rocketisp.stream_tubes import CoreStream

def calc_ODE_ODK_FROZ_isp(oxName='N2O4', fuelName='MMH',
                          Pc=1000.0, eps=10.0, pcentBell=80.0,Fvac=1000.0,
                          NumRuns=20, do_show=True):

    # ============ use RocketCEA to find MR range ===================
    mc = MR_Temperature_Limits( oxName=oxName, fuelName=fuelName,
                                PcNominal=Pc, epsNominal=eps)

    mr_peak = MR_Peak_At_EpsPc(mc, pc=Pc, eps=eps, ispType='CEAODE', # ispType can be CEAODE, CEAFROZEN
                               NterpSize=100)

    print('Peak IspODE=%g sec at MR ='%mr_peak.ispPeak,  mr_peak.mrPeak)
    print()
    print('MR at 97% Isp (on low  side) =', mr_peak.calc_mrLow_minus_NPcentIsp())
    print('MR at 97% Isp (on high side) =', mr_peak.calc_mrHigh_minus_NPcentIsp())

    mr_lo = round( mr_peak.mrLeftOfPeak - (mr_peak.mrRightOfPeak - mr_peak.mrLeftOfPeak)/10.0, 2)
    mr_hi = round( mr_peak.mrRightOfPeak, 2)
    delMR = (mr_hi - mr_lo) / (NumRuns - 1)

    # ===============================

    geomObj = Geometry(Rthrt=5.868/2,
                       CR=2.5, eps=eps,  pcentBell=pcentBell,
                       RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                       LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=16)

    core = CoreStream( geomObj, oxName=oxName, fuelName=fuelName,  MRcore=1.6,
                       Pc=Pc)

    R = RocketThruster(name='sample',coreObj=core, injObj=None)

    ispodeL = []
    ispodkL  = []
    ispodfL  = []
    mrL     = []

    MR = mr_lo
    for _ in range(NumRuns):
        mrL.append( MR )

        core.reset_attr( 'MRcore', MR, re_evaluate=True)
        R.scale_Rt_to_Thrust( Fvac, Pamb=0.0 , use_scipy=False )

        ispodeL.append( R.coreObj.IspODE )
        ispodkL.append( R.coreObj.IspODK )
        ispodfL.append( R.coreObj.IspODF )

        MR += delMR


    # ======= find peaks ======
    mr_ode_terp = InterpProp(mrL, ispodeL)
    mr_ode_Peak, isp_ode_peak = gold_search_max(mr_ode_terp, mrL[0], mrL[-1], tol=1.0e-5)

    mr_odk_terp = InterpProp(mrL, ispodkL)
    mr_odk_Peak, isp_odk_peak = gold_search_max(mr_odk_terp, mrL[0], mrL[-1], tol=1.0e-5)

    mr_odf_terp = InterpProp(mrL, ispodfL)
    mr_odf_Peak, isp_odf_peak = gold_search_max(mr_odf_terp, mrL[0], mrL[-1], tol=1.0e-5)


    fig, ax = plt.subplots( figsize=(8,6) )

    plt.plot(mrL, ispodeL, label='IspODE', color=COLORL[0])
    plt.plot(mrL, ispodkL, label='IspODK', color=COLORL[1])
    plt.plot(mrL, ispodfL, label='IspODF', color=COLORL[2])

    # show  ========= optimum MR difference ========
    def span_mrpeak( isL ):
        minpt = min(isL)
        maxpt = max(isL)
        span = maxpt - minpt
        return [maxpt-0.8*span, maxpt]

    plt.plot([mr_ode_Peak, mr_ode_Peak], span_mrpeak(ispodeL), '--', label='MRode=%.2f'%mr_ode_Peak, linewidth=2, color=COLORL[0])
    plt.plot([mr_odk_Peak, mr_odk_Peak], span_mrpeak(ispodkL), '--', label='MRodk=%.2f'%mr_odk_Peak, linewidth=2, color=COLORL[1])
    plt.plot([mr_odf_Peak, mr_odf_Peak], span_mrpeak(ispodfL), '--', label='MRodf=%.2f'%mr_odf_Peak, linewidth=2, color=COLORL[2])


    isp_odk_peak = abs(isp_odk_peak)
    plt.text( mr_odk_Peak, isp_odk_peak, '%i'%int(isp_odk_peak), ha='left', va='bottom', transform=ax.transData, color=COLORL[1]  )

    plt.legend()

    plt.ylabel('Isp (sec)')
    plt.xlabel('Mixture Ratio')

    plt.title( "%s/%s RocketIsp ODE ODK ODF\nFvac=%.0f lbf, Pc=%.0f psia, AR=%.0f:1, %%Bell=%.0f%%"%\
               (oxName, fuelName, Fvac, Pc, eps, pcentBell))

    png_name = 'odekf_%s_%s_Fvac%g_Pc%g_eps%g.png'%(oxName, fuelName, Fvac, Pc, eps)
    plt.savefig(png_name, dpi=120)

    if do_show:
        plt.show()


if __name__=="__main__":
    import sys
    if len(sys.argv)<6:
        calc_ODE_ODK_FROZ_isp( oxName='LOX', fuelName='LH2', Fvac=100000.0, Pc=2000.0, eps=10.0)
    else:
        oxName = sys.argv[1]
        fuelName = sys.argv[2]
        Fvac = float(sys.argv[3])
        Pc = float(sys.argv[4])
        eps = float(sys.argv[5])
        calc_ODE_ODK_FROZ_isp( oxName=oxName, fuelName=fuelName, Fvac=Fvac, Pc=Pc, eps=eps, do_show=False)

