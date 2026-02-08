from rocketisp.geometry import Geometry
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream
from rocketisp.rocket_isp import RocketThruster

C = CoreStream( geomObj=Geometry(eps=35),
                effObj=Efficiencies(ERE=0.99),
                oxName='LOX', fuelName='LH2',  MRcore=6,
                Pc=500, Pamb=0)

R = RocketThruster(name='Example 6K Thruster', coreObj=C)
R.scale_Rt_to_Thrust( 6000 , Pamb=0.0 )
R.summ_print()

