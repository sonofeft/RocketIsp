from rocketisp.geometry import Geometry
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream

C = CoreStream( geomObj=Geometry(eps=35), 
                effObj=Efficiencies(ERE=0.98, Noz=0.97), 
                oxName='LOX', fuelName='CH4',  MRcore=3.6,
                Pc=500, Pamb=14.7)

for name in ['IspODE','IspDel','IspODF']:
    print( '%8s ='%name, '%.1f'%C(name) )
print('%8s ='%'IspAmb','%.1f'%C('IspAmb'), C('noz_mode'))


C.summ_print()