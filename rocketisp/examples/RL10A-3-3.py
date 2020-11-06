"""
DESIGN REPORT
FOR
RLIOA-3-3 ROCKET ENGINE
CONTRACT NO. NAS 8-15494
Pratt & Whitney Aircraft
"""
xxx = 0
Fvac = 15000
MRcore = 5
Tc = xxx # R
Pc = 385.2 # psia
wdotFuel =  5.63 # lbm/sec
wdotOx   = 28.16 # lbm/sec

cstarEff = .986
cstar = 7626 # ft/sec
effCfODE = 0.98
Isp = 444 # sec
cstarODE = cstar / cstarEff # ft/sec
eps = 57.1
Lcham = 38.7

dpInjOx = 48.4
dpInjFuel = 81.8
CR = 83.4 / 20.75
At = 20.75
Rthrt = (At/3.14159)**0.5 # in

import sys
import os

sys.path.insert(0, os.path.abspath("../../"))  # needed to find rocketisp development version

from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
from rocketisp.stream_tubes import CoreStream
from rocketisp.efficiencies import Efficiencies
from rocketisp.examples.compare_vals import compare_header, compare
    
geomObj = Geometry(Rthrt=Rthrt,
                   CR=CR, eps=eps,  pcentBell=70, 
                   RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                   LchmOvrDt=2.4842/2, LchmMin=2.0, LchamberInp=Lcham)
                   
effObj = Efficiencies()
effObj.set_const('ERE', cstarEff )

core = CoreStream( geomObj, effObj, oxName='LOX', fuelName='LH2',  MRcore=MRcore,
                   Pc=Pc)
             
R = RocketThruster(name='RLIOA-3-3',coreObj=core, injObj=None,  noz_regen_eps=eps)
             
#R.scale_Rt_to_Thrust( Fvac, Pamb=0.0 , use_scipy=False )

compare_header()
compare('Fvacuum',Fvac, core('FvacTotal'))
compare('Isp Vacuum', Isp, core('IspDel'))
compare('Cstar ODE', cstarODE, core('cstarODE'))
compare('Efficiency Cf/Noz', effCfODE, effObj('Noz'))

print()
compare('Fuel Flow Rate', wdotFuel, core('wdotFlCore'))
compare('Ox Flow Rate', wdotOx, core('wdotOxCore'))



R.summ_print()
#geomObj.plot_geometry()
