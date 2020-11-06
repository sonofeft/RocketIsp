"""
model the Shuttle OMS
"""
from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
from rocketisp.stream_tubes import CoreStream
from rocketisp.efficiencies import Efficiencies
from rocketisp.examples.compare_vals import compare_header, compare

geomObj = Geometry(Rthrt=3,
                   CR=2.5, eps=55,  pcentBell=80, 
                   RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                   LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
                   
effObj = Efficiencies()
effObj.set_const('ERE', 0.97 )
core = CoreStream( geomObj=geomObj, effObj=effObj, 
                   oxName='N2O4', fuelName='MMH', 
                   MRcore=1.65, Pc=125 )
             
R = RocketThruster(name='Shuttle OMS',coreObj=core, injObj=None)
             
R.scale_Rt_to_Thrust( 6000 , Pamb=0.0 )

compare_header()
compare('Fvacuum',6000, core('FvacTotal'))
compare('Isp Vacuum', 313.2, core('IspDel'))
compare('Engine Length', 77, geomObj('Ltotal'))
compare('Nozzle ID', 43.09, geomObj('Rexit')*2)

R.summ_print()

