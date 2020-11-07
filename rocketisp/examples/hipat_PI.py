from rocketisp.geometry import Geometry
from rocketisp.examples.perfect_injector import PerfInjThruster

PI = PerfInjThruster( name='PI HiPAT', geomObj=Geometry(eps=375), ERE=0.99,
                      oxName='N2O4', fuelName='N2H4', MRcore=1.2, Pc=137,
                      isRegenCham=0, noz_regen_eps=1.0, calc_CdThroat=True)

PI.scale_Rt_to_Thrust( ThrustLbf=100.0, Pamb=0.0 )

MRcore_opt = PI.set_to_optimum_MR()
print('w/o FFC, MRcore_opt = %g'%MRcore_opt)


PI.summ_print()

