"""
model the XLR-134
"""
from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
from rocketisp.stream_tubes import CoreStream
from rocketisp.efficiencies import Efficiencies
    
geomObj = Geometry(Rthrt=1,
                   CR=3.0, eps=767.9,  pcentBell=80, 
                   RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                   LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
                   
effObj = Efficiencies()
effObj.set_const('ERE', (490.45-8.6)/490.45)
core = CoreStream( geomObj, effObj, oxName='LOX', fuelName='LH2',  MRcore=6.0,
                   Pc=510 )
             

R = RocketThruster(name='xlr134',coreObj=core, injObj=None)
             
R.scale_Rt_to_Thrust( 500 , Pamb=0.0 , use_scipy=False )
R.summ_print()

