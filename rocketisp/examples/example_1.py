"""
This example demonstrates the proper use of project: rocketisp
"""
from rocketisp.rocket_isp import RocketThruster

R = RocketThruster()
             
#R.scale_Rt_to_Thrust( 10000.0, Pamb=0.0, use_scipy=False )
R.summ_print()

