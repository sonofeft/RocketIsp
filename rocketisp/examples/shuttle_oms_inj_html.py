"""
model the Shuttle OMS
Create an HTML summary page and launch webbrowser to show summary.
"""
import webbrowser
import os


from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
from rocketisp.stream_tubes import CoreStream
from rocketisp.efficiencies import Efficiencies
from rocketisp.injector import Injector

from rocketisp.examples.compare_vals import compare_header, compare

geomObj = Geometry(Rthrt=3,
                   CR=2.5, eps=55,  pcentBell=80, 
                   RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                   LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
                   
effObj = Efficiencies()

core = CoreStream( geomObj=geomObj, effObj=effObj, 
                   oxName='N2O4', fuelName='MMH', 
                   MRcore=1.65, Pc=125, pcentFFC=10 )
I = Injector(core,
             Tox=None, Tfuel=None, elemEm=0.8,
             fdPinjOx=0.25, fdPinjFuel=0.25, dpOxInp=None, dpFuelInp=None,
             setNelementsBy='acoustics', # can be "acoustics", "elem_density", "input"
             OxOrfPerEl=1.0, FuelOrfPerEl=1.0, 
             lolFuelElem=False, 
             setAcousticFreqBy='mode', # can be "mode" or "freq"
             desAcousMode='2T', desFreqInp=5000, 
             CdOxOrf=0.75, CdFuelOrf=0.75, dropCorrOx=0.33, dropCorrFuel=0.33,
             DorfMin=0.008,
             LfanOvDorfOx=20.0, LfanOvDorfFuel=20.0)

R = RocketThruster(name='Shuttle OMS',coreObj=core, injObj=I)
             
R.scale_Rt_to_Thrust( 6000 , Pamb=0.0 )
R.set_MRthruster( MRthruster=1.65 )
R.scale_Rt_to_Thrust( 6000 , Pamb=0.0 )

compare_header()
compare('Fvacuum',6000, core('FvacTotal'))
compare('Isp Vacuum', 313.2, core('IspDel'))
compare('Engine Length', 77, geomObj('Ltotal'))
compare('Nozzle ID', 43.09, geomObj('Rexit')*2)

#R.summ_print()


fsave = 'shuttle_oms_inj.html'
fOut = open(fsave , 'w')
fOut.write( R.get_html_file_str() )
fOut.close()

#webbrowser.open( os.path.abspath(fsave) )

