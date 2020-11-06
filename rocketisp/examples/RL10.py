"""
RL-10  see: RL10_modeling.pdf
see RL10_perf_number.jpg
"""
xxx = 0
Fvac = 16412
MRcore = 5
Rthrt = 2.4724 # in
Tc = xxx # R
Pc = 475.5 # psia
wdotFuel =  6.161 # lbm/sec
wdotOx   = 30.76 # lbm/sec
thrust = xxx # lbf
cstarEff = xxx
cstar = xxx # ft/sec
Isp = 445.6 # sec
cstarODE = 93885 / 12.0 # ft/sec
eps=61
CdThroat = 0.975 # from: RL10_modeling.pdf

import sys
import os

sys.path.insert(0, os.path.abspath("../../"))  # needed to find rocketisp development version

from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
from rocketisp.stream_tubes import CoreStream
from rocketisp.efficiencies import Efficiencies
from rocketisp.examples.compare_vals import compare_header, compare
    
geomObj = Geometry(Rthrt=Rthrt,
                   CR=(5.131/2.4724)**2, eps=eps,  pcentBell=70, 
                   RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                   LchmOvrDt=2.4842/2, LchmMin=2.0, LchamberInp=15.0)
                   
effObj = Efficiencies()
effObj.set_const('ERE', 0.9892 )

core = CoreStream( geomObj, effObj, oxName='LOX', fuelName='LH2',  MRcore=MRcore,
                   Pc=Pc, CdThroat=CdThroat)
             
R = RocketThruster(name='RL10',coreObj=core, injObj=None, calc_CdThroat=False, noz_regen_eps=eps)
             
R.scale_Rt_to_Thrust( Fvac, Pamb=0.0 , use_scipy=False )

compare_header()
compare('Fvacuum',Fvac, core('FvacTotal'))
compare('Isp Vacuum', Isp, core('IspDel'))
compare('Cstar ODE', cstarODE, core('cstarODE'))
print()
compare('Fuel Flow Rate', wdotFuel, core('wdotFlCore'))
compare('Ox Flow Rate', wdotOx, core('wdotOxCore'))



R.summ_print()
#geomObj.plot_geometry()
