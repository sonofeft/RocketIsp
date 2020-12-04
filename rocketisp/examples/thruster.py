from rocketisp.geometry import Geometry
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream
from rocketisp.rocket_isp import RocketThruster
from rocketisp.injector import Injector


geomObj = Geometry(Rthrt=1,
                   CR=2.5, eps=20.0,  pcentBell=80, 
                   RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                   LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
                   
effObj = Efficiencies()

# It's an ablative chamber, so some FFC (fuel film cooling) is required... guess about 10%
C = CoreStream( geomObj=geomObj, effObj=effObj, pcentFFC=0.0, Pamb=0.0,
                oxName='N2O4', fuelName='MMH',  MRcore=1.9, Pc=500 )
                
I   = Injector(C, Tox=None, Tfuel=None, elemEm=0.8,
               fdPinjOx=0.25, fdPinjFuel=0.25,
               elemDensInp=None, NelementsInp=None,
               setNelementsBy='acoustics', # can be "acoustics", "density", "input"
               setAcousticFreqBy='mode', # can be "mode" or "freq"
               #desAcousMode=0.8*4.2012, desFreqInp=2000,
               desAcousMode='1T',
               OxOrfPerEl=1.0, FuelOrfPerEl=1.0, 
               lolFuelElem=True, 
               CdOxOrf=0.75, CdFuelOrf=0.75, dropCorrOx=1, dropCorrFuel=1,
               DorfMin=0.008,
               LfanOvDorfOx=20.0, LfanOvDorfFuel=20.0)


R = RocketThruster(name='Sample Thruster',coreObj=C, injObj=I, pulse_sec=float('inf'), pulse_quality=0.8)
R.set_mr_to_max_ispdel()


R.scale_Rt_to_Thrust( 6000 , Pamb=0.0 )
R.coreObj.effObj.summ_print()

