from rocketisp.geometry import Geometry
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream
from rocketisp.rocket_isp import RocketThruster

# create CoreStream with area ratio=375:1, Pc=137, FFC=30% and effERE=0.99
C = CoreStream( geomObj=Geometry(eps=375), 
                effObj=Efficiencies(ERE=0.99), pcentFFC=30,
                oxName='N2O4', fuelName='N2H4',  MRcore=1.26 ,
                Pc=137, Pamb=0)

# instantiate RocketThruster
R = RocketThruster(name='100 lbf Aerojet HiPAT R-4D', coreObj=C)

R.scale_Rt_to_Thrust( 100 , Pamb=0.0 )


MRcore_opt = R.set_mr_to_max_ispdel()
print('MRcore_opt = %g'%MRcore_opt)

R.summ_print()

