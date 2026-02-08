import os
from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
# from rocketisp.injector import Injector
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream
from rocketcea.biprop_utils.mr_t_limits import MR_Temperature_Limits
from rocketcea.biprop_utils.mr_peak_at_eps_pc import MR_Peak_At_EpsPc


if 'READTHEDOCS' not in os.environ:
    from rocketcea.cea_obj import CEA_Obj
    from rocketcea.separated_Cf import sepNozzleCf
else:
    from rocketisp.mock.cea_obj import CEA_Obj
    from rocketisp.mock.separated_Cf import sepNozzleCf

""" =============== info from Gemini ==================
1. Gas Temperature at the Wall (by Cooling Type)
This table represents the temperature of the boundary layer gas immediately in contact with the chamber wall.
+----------------+----------------------+-----------------------------------+
| Cooling Method | Wall Gas Temp Range  | Primary Material Limit            |
+----------------+----------------------+-----------------------------------+
| Ablative       | 500°C to 1,100°C     | ***Tgas includes Pyrolysis gas*** | 1400R to 2500R (1950 R ave)
+----------------+----------------------+-----------------------------------+
| Radiation      | 1,200°C to 1,600°C   | Melting point of refractory metal | 2650R to 3350R (3000 R ave)
+----------------+----------------------+-----------------------------------+
| Regenerative   | 600°C to 1,000°C     | Thermal fatigue of wall liner     | 1575R to 2300R (~1950 R ave)
+----------------+----------------------+-----------------------------------+

Sources and Technical References
Cooling Method Typical Wall Gas Temp Source/Technical Basis

Ablative 500°C to 1,100°C Sutton & Biblarz, Rocket Propulsion Elements: 
Describes the charring of phenolic resins. Pyrolysis begins at low temperatures (~400°C), 
and the protective boundary layer formed by the outgassing keeps the wall gas significantly 
cooler than the core ($3,000C+).

Radiation 1,200°C to 1,600°C Huzel & Huang, Design of Liquid Propellant Rocket Engines: 
Notes that radiation-cooled thrusters (e.g., Niobium/C-103) must operate at "white heat" 
to balance heat flux via the Stefan-Boltzmann law (q goes like T**4).
The material's reuse limit is typically near $1,400C - 1,500C.

Regenerative 600°C to 1,000°C NASA SP-8087, Liquid Rocket Engine Fluid-Cooled Combustion Chambers: 
This range represents the gas-side wall temperature achievable when using film cooling in 
conjunction with active regenerative cooling to prevent the copper liner from exceeding 
its structural "softening" point (usually $<600C).
...............
NASA SP-8124 Self-Cooled Combustion Chambers

Ablative Chambers.
 - Keep wall temperature below 3000F (3460R).
Use 3400R in RocketIsp for aggressive ablative (3000R to be conservative) 

.............
=== more Gemini data ===
Cooling Type,   Material Class,             Key Material Example,Max Operating Temp (Material)
Ablative,       Reinforced Polymers,        Carbon-Phenolic,    "~2,500°C (Surface)"   5000 R
Radiation,      Refractory Metals,          Niobium (C-103),    "~1,400°C - 1,600°C"   3000 R to 3350 R
Regenerative,   High-Conductivity Alloys,   GRCop-42 (Copper),  ~500°C - 800°C         1400 R to 2000 R
"""

    
def get_thruster_basic( name="basic engine",  
                oxName='N2O4', fuelName='MMH', 
                cooling_design='ablative', # can be ablative, radiation, regen
                Pc=150.0, Fvac=100.0, eps=50.0, 
                MRcore=None, MRthruster=None, pcentFFC=None, TwallGasReqmt=2800.0,
                CR=2.5, LchmOvrDt=4.0, LchamMin=1.5 , LchamberInp=None,
                etaERE=0.98, 
                pcentBell=80.0, Pamb=0.0,
                pulse_sec=float('inf'), pulse_quality=0.8):
    

    ceaObj = CEA_Obj(oxName=oxName, fuelName=fuelName)

    geomObj = Geometry(Rthrt=5.868/2,
                    CR=CR, eps=eps,  pcentBell=pcentBell, 
                    RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                    LchmOvrDt=LchmOvrDt, LchmMin=LchamMin, LchamberInp=LchamberInp)
    
    effObj = Efficiencies()
    effObj.set_const('ERE', etaERE)

    mc = MR_Temperature_Limits( oxName=oxName, fuelName=fuelName,
                                PcNominal=Pc, epsNominal=eps)

    mr_peak_obj = MR_Peak_At_EpsPc(mc, pc=Pc, eps=eps, ispType='CEAODE', # ispType can be CEAODE, CEAFROZEN
                                    NterpSize=100)

    if MRcore is None:
        MRcore = mr_peak_obj.mrPeak
    
    core = CoreStream( geomObj, effObj, oxName=oxName, fuelName=fuelName,  MRcore=MRcore,
                Pc=Pc, CdThroat=0.995,
                pcentFFC=14.0, ko=0.035)
    
    rocket = RocketThruster(name=name, coreObj=core,  pulse_sec=pulse_sec, pulse_quality=pulse_quality)

    rocket.scale_Rt_to_Thrust( Fvac, Pamb=Pamb)


    return rocket 

def dev_tests():
    rocket = get_thruster_basic()

    rocket.summ_print()

if __name__ == "__main__":

    dev_tests()

