"""
model the A-1 Engine example from:
MODERN ENGINEERING FOR DESIGN OF LIQUID-PROPELLANT ROCKET ENGINES 
by:Dieter K. Huzel and David H. Huang 
page 58. (some calculations from page 71 apply) (76 and 88 in PDF)
"""
import sys
import os

sys.path.insert(0, os.path.abspath("../../"))  # needed to find rocketisp development version
from math import pi
from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
from rocketisp.stream_tubes import CoreStream
from rocketisp.injector import Injector
from rocketisp.efficiencies import Efficiencies
from rocketisp.examples.compare_vals import compare_header, compare

xxx = 0
Fvac = 149500 # lbf for thrust chamber w/o gas generator flow
Isp = 440 # sec
CfVacDesign = 1.895

oxName = 'LOX'
fuelName = 'LH2'
Pc = 800 # psia
wdFuel = 54.5
wdOx = 285.2
wdFuelEngine = 57.6
wdOxEngine =  288
#wdRatio = (wdFuel + wdOx) / (wdFuelEngine + wdOxEngine)
#print('wdCore/wdEngine=%g,  IspEngine/IspCore=%g'%( wdRatio, 262.4/270 ))

MR = 5.22
pcentBell = 75

cstar = 7480 # ft/sec
effCstar = .975
cstarODE = cstar / effCstar

effCfFrozen = 1.01 # based on FROZEN Isp
eps = 40
CR = 1.6
Lcham = 26 # in
At = 98.6 # in**2
Rt = (At / pi)**0.5
#print( 'Calculated MR =', wdOx / wdFuel )

dpOxInp=160
dpFuelInp=100

geomObj = Geometry(Rthrt=Rt,
                   CR=CR, eps=eps,  pcentBell=pcentBell, 
                   RupThroat=0.5, RdwnThroat=1.0, RchmConv=0.5, cham_conv_deg=30,
                   LchmOvrDt=3, LchmMin=2.0, LchamberInp=Lcham)
                   
effObj = Efficiencies()
effObj.set_const('ERE', 0.975 )

core = CoreStream( geomObj, effObj, oxName=oxName, fuelName=fuelName,  MRcore=MR,
             Pc=Pc, Pamb=14.7, CdThroat=1.0, 
             adjCstarODE=0.992801, adjIspIdeal=1.01876)

C = RocketThruster(name='Huzel A-2',coreObj=core, injObj=None, calc_CdThroat=False)
             
#C.scale_Rt_to_Thrust( Fvac, Pamb=0 , use_scipy=False )

compare_header()

compare('Fvacuum',Fvac, core('FvacTotal'))

compare('CfVacDesign', CfVacDesign, core('CfVacDel'))
print()

compare('Efficiency Cstar/ERE', effCstar, effObj('ERE'))
compare('Cstar ODE', cstarODE, core('cstarODE'))
compare('Cstar Delivered', cstar, core('cstarERE'))

effCfODE = effCfFrozen * core('IspODF') / core('IspODE')
compare('Efficiency Cf/Noz', effCfODE, effObj('Noz'))

print()
compare('Isp Vacuum', Isp, core('IspDel'))

IspFrozen = Isp / effCstar / effCfFrozen
compare('IspODF', IspFrozen, core('IspODF'))

compare('Throat Area', At, geomObj('At'))
compare('Fuel Flow Rate', wdFuel, core('wdotFlCore'))
compare('Ox Flow Rate', wdOx, core('wdotOxCore'))

C.summ_print()

