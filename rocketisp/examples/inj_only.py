from rocketisp.geometry import Geometry
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream
from rocketisp.injector import Injector

G = Geometry(Rthrt=5.978,
             CR=2.5, eps=62.5,  pcentBell=75, 
             RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
             LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
             
C = CoreStream( geomObj=G, effObj=Efficiencies(ERE=0.98, Noz=0.96515),  pcentFFC=10.0,
                oxName='N2O4', fuelName='A50',  MRcore=1.6, Pc=100, Pamb=0.0 )

I = Injector(C,
             Tox=None, Tfuel=None, elemEm=0.8,
             fdPinjOx=0.25, fdPinjFuel=0.25, dpOxInp=None, dpFuelInp=None,
             setNelementsBy='acoustics', # can be "acoustics", "elem_density", "input"
             elemDensInp=5, NelementsInp=100,
             OxOrfPerEl=1.0, FuelOrfPerEl=1.0, 
             lolFuelElem=True, 
             setAcousticFreqBy='mode', # can be "mode" or "freq"
             desAcousMode='2T', desFreqInp=5000, 
             CdOxOrf=0.75, CdFuelOrf=0.75, dropCorrOx=0.33, dropCorrFuel=0.33,
             DorfMin=0.008,
             LfanOvDorfOx=20.0, LfanOvDorfFuel=20.0)

I.summ_print( show_core_stream=False )

