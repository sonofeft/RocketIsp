"""
model the J-2
"""
import sys
import os

sys.path.insert(0, os.path.abspath("../../"))  # needed to find rocketisp development version

from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
from rocketisp.stream_tubes import CoreStream
from rocketisp.efficiencies import Efficiencies
from rocketisp.examples.compare_vals import compare_header, compare

xxx = 0
Fvac = 232250
FseaLevel = 109302 # lbf

MRcore = 5.5
Rthrt = 7.323 # in
Tc = xxx # R
Pc = 736 # psia
wdotFuel =  xxx # lbm/sec
wdotOx   = xxx # lbm/sec

cstarEff = xxx
cstar = xxx # ft/sec
Isp = 421 # sec
IspSL = 200 # sec
cstarODE = xxx / 12.0 # ft/sec
eps = 25
CR = 2.5


geomObj = Geometry(Rthrt=Rthrt,
                   CR=CR, eps=eps,  pcentBell=80, 
                   RupThroat=1.0, RdwnThroat=0.392, RchmConv=1.5, cham_conv_deg=30,
                   LchmOvrDt=2.5, LchmMin=2.0, LchamberInp=None)
                   
effObj = Efficiencies()
effObj.set_const('ERE', 0.99 )

core = CoreStream( geomObj, effObj, oxName='LOX', fuelName='LH2',  MRcore=MRcore,
                   Pc=Pc)
             

R = RocketThruster(name='J-2',coreObj=core, injObj=None, 
                   pulse_sec=float('inf'), pulse_quality=0.8)
             
#R.scale_Rt_to_Thrust( Fvac , Pamb=0.0  , use_scipy=False )

compare_header()
compare('Fvacuum',Fvac, core('FvacTotal'))
compare('Isp Vacuum', Isp, core('IspDel'))

core.reset_attr( 'Pamb', 14.7, re_evaluate=True)
compare('Isp SeaLevel', IspSL, core('IspAmb'))
compare('FseaLevel', FseaLevel, core('Fambient'))
core.reset_attr( 'Pamb', 0, re_evaluate=True)

compare('Cstar ODE', cstarODE, core('cstarODE'))
print()
compare('Fuel Flow Rate', wdotFuel, core('wdotFlCore'))
compare('Ox Flow Rate', wdotOx, core('wdotOxCore'))

R.summ_print()

