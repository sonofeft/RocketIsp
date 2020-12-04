"""
model the A-1 Engine example from:
MODERN ENGINEERING FOR DESIGN OF LIQUID-PROPELLANT ROCKET ENGINES 
by:Dieter K. Huzel and David H. Huang 
page 61. (some calculations from page xxx apply)
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
Fvac = 16000 # lbf for thrust chamber w/o gas generator flow
Isp = 446 # sec
CfVacDesign = 1.817

oxName = 'F2'
fuelName = 'LH2'
Pc = 100 # psia
wdFuel = 5.13
wdOx = 30.78

MR = 6
pcentBell = 70
cstar = 7910 # ft/sec
effCstar = .98
cstarODE = cstar / effCstar

effCfFrozen = 1.02 # based on FROZEN Isp
eps = 35
CR = 2
Lcham = 28 # in
At = 88 # in**2
Rt = (At / pi)**0.5
#print( 'Calculated MR =', wdOx / wdFuel )

dpOxInp=25
dpFuelInp=25

geomObj = Geometry(Rthrt=Rt,
                   CR=CR, eps=eps,  pcentBell=pcentBell, 
                   RupThroat=0.5, RdwnThroat=1.0, RchmConv=0.5, cham_conv_deg=30,
                   LchmOvrDt=3, LchmMin=2.0, LchamberInp=Lcham)
                   
effObj = Efficiencies()
#effObj.set_const('ERE', 0.98 )


core = CoreStream( geomObj, effObj, oxName=oxName, fuelName=fuelName,  MRcore=MR,
             Pc=Pc, Pamb=14.7, CdThroat=1.0, 
             adjCstarODE=0.969237, adjIspIdeal=1.02338)

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

C = RocketThruster(name='Huzel A-3',coreObj=core, injObj=inj, calc_CdThroat=False)
             
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

