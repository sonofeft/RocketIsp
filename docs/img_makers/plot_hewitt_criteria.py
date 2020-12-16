import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

from plothelp.plot_help import Figure, sample_data, Curve, CWheel, plt
import numpy as np

from rocketisp.rocket_isp import RocketThruster
from rocketisp.geometry import Geometry
from rocketisp.stream_tubes import CoreStream
from rocketisp.efficiencies import Efficiencies
from rocketisp.injector import Injector, modeSvnD

geomObj = Geometry(Rthrt=3,
                   CR=2.5, eps=55,  pcentBell=80, 
                   RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                   LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
                   
effObj = Efficiencies()

core = CoreStream( geomObj=geomObj, effObj=effObj, 
                   oxName='N2O4', fuelName='MMH', 
                   MRcore=1.65, Pc=125, pcentFFC=10 )
I = Injector(core,
             Tox=None, Tfuel=None, elemEm=0.8,
             fdPinjOx=0.25, fdPinjFuel=0.25, dpOxInp=None, dpFuelInp=None,
             setNelementsBy='acoustics', # can be "acoustics", "elem_density", "input"
             OxOrfPerEl=1.0, FuelOrfPerEl=1.0, 
             lolFuelElem=False, 
             setAcousticFreqBy='mode', # can be "mode" or "freq"
             desAcousMode='2T', desFreqInp=5000, 
             CdOxOrf=0.75, CdFuelOrf=0.75, dropCorrOx=0.33, dropCorrFuel=0.33,
             DorfMin=0.008,
             LfanOvDorfOx=20.0, LfanOvDorfFuel=20.0)

R = RocketThruster(name='Shuttle OMS',coreObj=core, injObj=I)
             
R.scale_Rt_to_Thrust( 6000 , Pamb=0.0 )
R.set_MRthruster( MRthruster=1.65 )
R.scale_Rt_to_Thrust( 6000 , Pamb=0.0 )
#R.summ_print()
        

# ========================================================
CWheel.set_wheel( 'tab10' )


title = "Hewitt Criteria\nAnchored with Strouhal Number = 0.2"

F = Figure( figsize=(6,5), dpi=300, nrows=1, ncols=1,
            sharex=False, sharey=False, hspace=None, wspace=None,
            title=title, show_grid=True, tight_layout=True,
            png_path_name= os.path.join(up_one, '_static', 'hewitt_derived.png' ) )

F.set_x_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)
F.set_y_number_format(major_fmt='.1f', major_size=10, minor_fmt='', minor_size=8)

curveL = []
dovL = [1E-5, 1E-4, 1E-3]
xpos_label = 5E-4
dyD = {'1T':3.5, '2T':4.5, '3T':9}

for i, mode in enumerate( ['1T', '2T', '3T'] ):
    Svn = modeSvnD[mode]
    DinjL = []
    for dov in dovL:
        d = dov * R.injObj.sonicVel
    
        # freq = Svn * R.injObj.sonicVel / pi / (D/12.0)
        # self.des_freq = self.strouhal_mult * velFl_ips / self.DorfFuel
        freq = 0.2 * (R.injObj.sonicVel*12.0) / d
        D = Svn * R.injObj.sonicVel * 12.0 / ( freq )
        print('mode=%s, d=%g, D=%g'%(mode, d, D) )
        DinjL.append( D )
        
    curve = Curve(plot_type='loglog', xL=dovL, yL=DinjL, marker='',
                  label=mode, linewidth=3, dy_placement=dyD[mode], linecolor=CWheel(i),
                  place_labels_on_line=True, xpos_label=xpos_label)              
    curveL.append( curve )
    
chart = F.add_chart( row=0, col=0, curveL=curveL, 
                     xlabel='d/V (in/ft/s)', 
                     ylabel='Chamber Diameter (in)', ymax=100,
                     show_legend=True, legend_loc='lower right' )
              


F.make( do_show=True )




