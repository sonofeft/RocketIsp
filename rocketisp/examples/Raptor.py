"""
model the SpaceX Raptor
"""
from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
from rocketisp.stream_tubes import CoreStream
from rocketisp.efficiencies import Efficiencies
from rocketisp.examples.compare_vals import compare_header, compare

geomObj = Geometry(Rthrt=4,
                   CR=2.5, eps=40,  pcentBell=90, 
                   RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                   LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
                   
effObj = Efficiencies()

core = CoreStream( geomObj=geomObj, effObj=effObj, 
                   oxName='LOX', fuelName='CH4', 
                   MRcore=3.6, Pc=4786 )
             
R = RocketThruster(name='SpaceX Raptor',coreObj=core, injObj=None)
             
R.scale_Rt_to_Thrust( 500000 , Pamb=0.0 )


compare_header()
compare('Fvacuum',500000, core('FvacTotal'))
compare('Isp Vacuum', 380, core('IspDel'))

core.reset_attr( 'Pamb', 14.7, re_evaluate=True)
compare('Isp SeaLevel', 330, core('IspAmb'))
core.reset_attr( 'Pamb', 0, re_evaluate=True)


R.summ_print()

