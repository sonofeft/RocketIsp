import os
from rocketisp.geometry import Geometry
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream
from rocketisp.injector import Injector
from rocketisp.rocket_isp import RocketThruster

C = CoreStream( geomObj=Geometry(eps=75), 
                effObj=Efficiencies(), pcentFFC=15,
                oxName='N2O4', fuelName='N2H4',  MRcore=1.26 ,
                Pc=137, Pamb=0)
                
I = Injector( C )

# instantiate RocketThruster
R = RocketThruster(name='100 lbf Engine', coreObj=C, injObj=I)

R.scale_Rt_to_Thrust( 100 , Pamb=0.0 )

here = os.path.split( os.path.abspath(__file__) )[0]
fOut = open( os.path.join(here, 'chk_html_save.html'), 'w')
fOut.write( R.get_html_file_str() )
print( os.path.abspath( fOut.name ) )
fOut.close()

print('SAVED: chk_html_save.html to:', os.path.abspath( fOut.name ))


