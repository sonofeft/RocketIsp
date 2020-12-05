"""
Apollo SPS, Aerojet AJ10-137 (Apollo Service Module Engine)
Create an HTML summary page and launch webbrowser to show it.
"""
import webbrowser
import os
from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
from rocketisp.stream_tubes import CoreStream
from rocketisp.efficiencies import Efficiencies

# create basic Geometry. 
# Use "place-holder" of 1 inch for throat radius... correct later with "scale_Rt_to_Thrust"
geomObj = Geometry(Rthrt=1,
                   CR=2.5, eps=62.5,  pcentBell=72.3, 
                   RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                   LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
                   
effObj = Efficiencies()
effObj.set_const('ERE', 0.98) # don't know injector details so set effERE=0.98

# It's an ablative chamber, so some FFC (fuel film cooling) is required... guess about 15%
core = CoreStream( geomObj=geomObj, effObj=effObj, pcentFFC=15.0,
                   oxName='N2O4', fuelName='A50',  MRcore=1.6, Pc=100 )
             
R = RocketThruster(name='Apollo SPS',coreObj=core)

# scale geometry to give 20,500 lbf of thrust for current conditions
R.scale_Rt_to_Thrust( 20500 , Pamb=0.0  )

# figure out best mixture ratio to run the engine.
R.set_mr_to_max_ispdel()

# re-scale geometry to give 20,500 lbf of thrust after MR change
R.scale_Rt_to_Thrust( 20500 , Pamb=0.0  )
            
fsave = 'Apollo_SPS.html'
fOut = open(fsave , 'w')
fOut.write( R.get_html_file_str() )
fOut.close()

webbrowser.open( os.path.abspath(fsave) )


