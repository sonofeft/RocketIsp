import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

import numpy as np
from plothelp.plot_help import Figure, sample_data, Curve, CWheel
from rocketcea.biprop_utils.InterpProp_scipy import InterpProp
from rocketcea.biprop_utils.goldSearch import search_max as gold_search_max
from rocketcea.biprop_utils.mr_t_limits import MR_Temperature_Limits
from rocketcea.biprop_utils.mr_peak_at_eps_pc import MR_Peak_At_EpsPc

from rocketisp.geometry import Geometry
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream
from rocketisp.rocket_isp import RocketThruster


oxName = 'N2O4'
fuelName = 'MMH'
Fvac = 100 # lbf
Pc = 100 # psia
eps = 100 
pcentBell = 80

mc = MR_Temperature_Limits( oxName=oxName, fuelName=fuelName, 
                            PcNominal=Pc, epsNominal=eps, 
                            TC_LIMIT=1000.0, MR_MIN=0.0, MR_MAX=1000.0)

mr_peak = MR_Peak_At_EpsPc(mc, pc=Pc, eps=eps, ispType='CEAODE', # ispType can be CEAODE, CEAFROZEN
                           NterpSize=100)
                           
print('Peak IspODE=%g sec at MR ='%mr_peak.ispPeak,  mr_peak.mrPeak)
print() 
print('MR at 97% Isp (on low  side) =', mr_peak.calc_mrLow_minus_NPcentIsp())
print('MR at 97% Isp (on high side) =', mr_peak.calc_mrHigh_minus_NPcentIsp())

mr_lo = round( mr_peak.mrLeftOfPeak - (mr_peak.mrRightOfPeak - mr_peak.mrLeftOfPeak)/10.0, 2)
mr_hi = round( mr_peak.mrRightOfPeak, 2)
print('mr_lo =',mr_lo)
print('mr_hi =',mr_hi)

# =========== create RocketIsp structures
# create CoreStream with area ratio=375:1, Pc=137, FFC=30% and effERE=0.99
C = CoreStream( geomObj=Geometry(eps=eps), 
                effObj=Efficiencies(ERE=1.0, Div=1.0, BL=1.0, TP=1.0), pcentFFC=0,
                oxName=oxName, fuelName=fuelName,  MRcore=mr_lo,
                Pc=Pc, Pamb=0)

# instantiate RocketThruster
R = RocketThruster(name='Sample Thruster', coreObj=C)
R.scale_Rt_to_Thrust( ThrustLbf=Fvac, Pamb=0.0)
#R.summ_print()
# =========================================================
# generate data
ispodeL  = [] # list of IspODE  (one-dimensional equilibrium)
ispodkL  = [] # list of IspODK  (one-dimensional kinetic)
ispodfL  = [] # list of IspODF  (frozen)
mrcoreL  = [] # list of MRcore  (core stream tube mixture ratio)
for MRcore in np.linspace( mr_lo, mr_hi, num=60 ):
    C.reset_attr( 'MRcore', MRcore )
    R.scale_Rt_to_Thrust( Fvac , Pamb=0.0 )

    ispodeL.append( C('IspODE') )
    ispodkL.append( C('IspODK') )
    ispodfL.append( C('IspODF') )
    mrcoreL.append( C('MRcore') )

# ========================================================
# ======= find peaks ======
mr_ode_terp = InterpProp(mrcoreL, ispodeL)
mr_ode_Peak, isp_ode_peak = gold_search_max(mr_ode_terp, mrcoreL[0], mrcoreL[-1], tol=1.0e-5)
isp_ode_peak = -isp_ode_peak
print('mr_ode_Peak, isp_ode_peak',mr_ode_Peak, isp_ode_peak)

mr_odk_terp = InterpProp(mrcoreL, ispodkL)
mr_odk_Peak, isp_odk_peak = gold_search_max(mr_odk_terp, mrcoreL[0], mrcoreL[-1], tol=1.0e-5)
isp_odk_peak = -isp_odk_peak
print('mr_odk_Peak, isp_odk_peak',mr_odk_Peak, isp_odk_peak)

mr_odf_terp = InterpProp(mrcoreL, ispodfL)
mr_odf_Peak, isp_odf_peak = gold_search_max(mr_odf_terp, mrcoreL[0], mrcoreL[-1], tol=1.0e-5)
isp_odf_peak = -isp_odf_peak
print('mr_odf_Peak, isp_odf_peak',mr_odf_Peak, isp_odf_peak)

# ========================================================
CWheel.set_wheel( 'tab10' )


title = '%s/%s Peak Isp ODE, ODK, ODF\n'%(oxName, fuelName) +\
        'Fvac=%g lbf, Pc=%g psia, AR=%g:1, %%Bell=%g'%(Fvac, Pc, eps, pcentBell)

F = Figure( figsize=(6,5), dpi=300, nrows=1, ncols=1,
            sharex=False, sharey=False, hspace=None, wspace=None,
            title=title, show_grid=True, tight_layout=True,
            png_path_name= os.path.join(up_one, '_static', 'odekf_%s_%s.png'%(oxName, fuelName)  ) )

F.set_x_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)
F.set_y_number_format(major_fmt='.1f', major_size=10, minor_fmt='', minor_size=8)

curveL = []
xpos_label = mrcoreL[-9]
peakL = [(mr_ode_Peak, isp_ode_peak), (mr_odk_Peak, isp_odk_peak), (mr_odf_Peak, isp_odf_peak)]

for i, (label, yL) in enumerate( [('IspODE',ispodeL), ('IspODK',ispodkL), ('IspODF',ispodfL)] ):
    curve = Curve(plot_type='plot', xL=mrcoreL, yL=yL, marker='',
                  label=label, linewidth=3, dy_placement='3%', linecolor=CWheel(i),
                  place_labels_on_line=True, xpos_label=xpos_label)              
    curveL.append( curve )
    
    mrpeak, isppeak = peakL[i] # '%.2f, %.0f'%(mrpeak, isppeak)
    curve = Curve(plot_type='plot', xL=[mrpeak, mrpeak+0.00001], yL=[isppeak-10, isppeak], marker='',
                  label='%.2f'%(mrpeak, ), linewidth=1, dy_placement='3%', linecolor=CWheel(i),
                  dx_placement='-2%',
                  place_labels_on_line=True, xpos_label=mrpeak+0.00001/2, linestyle='--')              
    curveL.append( curve )
    
    curve.add_extra_text(xpos_label=mrpeak, ypos_label=isppeak, dy_placement='3%', 
                         label='%.0f'%isppeak, abs_angle=0)

    
chart = F.add_chart( row=0, col=0, curveL=curveL, 
                     xlabel='Mixture Ratio', 
                     ylabel='Isp (sec)', ymax=(isp_ode_peak+10),
                     show_legend=True, legend_loc='lower right' )
              


F.make( do_show=True )

