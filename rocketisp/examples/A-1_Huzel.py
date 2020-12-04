"""
model the A-1 Engine example from:
MODERN ENGINEERING FOR DESIGN OF LIQUID-PROPELLANT ROCKET ENGINES 
by:Dieter K. Huzel and David H. Huang 
page 54. (some calculations from pages 67-70 apply)
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

FseaLevel = 747000 # lbf for thrust chamber w/o gas generator flow
Isp = 270 # sec
CfVacDesign = 1.768
CfAmbDel = 1.562
oxName = 'LOX'
fuelName = 'RP1'
Pc = 1000 # psia
wdFuel = 827
wdOx = 1941
wdFuelEngine = 892.3
wdOxEngine =  1967.7
wdRatio = (wdFuel + wdOx) / (wdFuelEngine + wdOxEngine)
#print('wdCore/wdEngine=%g,  IspEngine/IspCore=%g'%( wdRatio, 262.4/270 ))

MR = 2.35
pcentBell = 80

cstar = 5660 # ft/sec
effCstar = 0.975
cstarODE = cstar / effCstar

effCfFrozen = 0.98 # based on FROZEN Isp
eps = 14
CR = 1.6
Lcham = 45 # in
At = 487 # in**2
Rt = (At / pi)**0.5
#print( 'Calculated MR =', wdOx / wdFuel )

dpOxInp=200
dpFuelInp=200

geomObj = Geometry(Rthrt=Rt,
                   CR=CR, eps=eps,  pcentBell=pcentBell, 
                   RupThroat=0.5, RdwnThroat=1.0, RchmConv=0.5, cham_conv_deg=30,
                   LchmOvrDt=3, LchmMin=2.0, LchamberInp=Lcham)
                   
effObj = Efficiencies()
#effObj.set_const('ERE', 0.975 )
effObj.set_const('Noz', 0.933177 ) # Huzel based on frozen Isp

core = CoreStream( geomObj, effObj, oxName=oxName, fuelName=fuelName,  MRcore=MR,
             Pc=Pc, Pamb=14.7, CdThroat=1.0, 
             adjCstarODE=0.978196, adjIspIdeal=1.0084418978404621)

inj = Injector(core, Tox=None, Tfuel=None, elemEm=0.8, 
               fdPinjOx=0.2, fdPinjFuel=0.2, dpOxInp=dpOxInp, dpFuelInp=dpFuelInp,
               elemDensInp=None, NelementsInp=None,
               setNelementsBy='acoustics', # can be "acoustics", "density", "input"
               setAcousticFreqBy='mode', # can be "mode" or "freq"
               desAcousMode='2T', desFreqInp=None,
               OxOrfPerEl=1.0, FuelOrfPerEl=1.0, 
               lolFuelElem=True, 
               CdOxOrf=0.75, CdFuelOrf=0.75, dropCorrOx=0.33, dropCorrFuel=0.33,
               pcentFFC=None, DorfMin=0.008,
               LfanOvDorfOx=20.0, LfanOvDorfFuel=20.0)


C = RocketThruster(name='Huzel A-1',coreObj=core, injObj=inj, calc_CdThroat=False)
             
#C.scale_Rt_to_Thrust( FseaLevel, Pamb=15 , use_scipy=False )

compare_header()

compare('FseaLevel',FseaLevel, core('Fambient'))

compare('CfVacDesign', CfVacDesign, core('CfVacDel'))
compare('CfAmbDel', CfAmbDel, core('CfAmbDel'))
print()

compare('Efficiency Cstar/ERE', effCstar, effObj('ERE'))
compare('Cstar ODE', cstarODE, core('cstarODE'))
compare('Cstar Delivered', cstar, core('cstarERE'))


effCfODE = effCfFrozen * core('IspODF') / core('IspODE')
compare('Efficiency Cf/Noz', effCfODE, effObj('Noz'))
print()
compare('IspseaLevel', Isp, core('IspAmb'))

IspFrozen = Isp * ( core('FvacTotal') / core('Fambient') ) / effCstar / effCfFrozen
compare('IspODF', IspFrozen, core('IspODF'))

compare('Throat Area', At, geomObj('At'))
compare('Fuel Flow Rate', wdFuel, core('wdotFlCore'))
compare('Ox Flow Rate', wdOx, core('wdotOxCore'))

C.summ_print()

