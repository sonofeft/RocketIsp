import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

from rocketisp.geometry import Geometry
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream
from rocketisp.injector import Injector
from rocketisp.rocket_isp import RocketThruster
import numpy as np
from plothelp.plot_help import Figure, sample_data, Curve, plt

F = Figure( figsize=(5,4), dpi=300, nrows=1, ncols=1,
            sharex=False, sharey=False, hspace=None, wspace=None,
            title='Mixing Efficiency\n(as function of element density)', 
            show_grid=True, tight_layout=True,
            png_path_name= os.path.join(up_one, '_static', 'mixing_eff.png') )

F.set_x_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)
F.set_y_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)

curveL = []

EFF_MIN = 0.85
LchamArr = np.linspace(1.5, 10, 50)
edensL = [2,5,10,20]

xposL = [5.6, 4, 3.35, 2.85]
dangL = [0,0,0, 5]
for ie,elemDensInp in enumerate(edensL):
    
    effMixL = []
    lchamL = []

    for LchamberInp in LchamArr:
        geomObj = Geometry(Rthrt=3,
                           CR=2.0, eps=55,  pcentBell=80, 
                           RupThroat=0.05, RdwnThroat=1.0, RchmConv=0.05, cham_conv_deg=50,
                           LchmOvrDt=3.10, LchmMin=0.01, LchamberInp=LchamberInp)
                           
        effObj = Efficiencies()
        #effObj.set_const('ERE', 0.97 )
        C = CoreStream( geomObj=geomObj, effObj=effObj, 
                        oxName='N2O4', fuelName='MMH', 
                        MRcore=1.65, Pc=125 )

        I = Injector(C,
                     Tox=None, Tfuel=None, elemEm=0.8,
                     fdPinjOx=0.25, fdPinjFuel=0.25, dpOxInp=None, dpFuelInp=None,
                     setNelementsBy='elem_density', # can be "acoustics", "elem_density", "input"
                     elemDensInp=elemDensInp, NelementsInp=100,
                     OxOrfPerEl=1.0, FuelOrfPerEl=1.0, 
                     lolFuelElem=True, 
                     setAcousticFreqBy='mode', # can be "mode" or "freq"
                     desAcousMode='2T', desFreqInp=5000, 
                     CdOxOrf=0.75, CdFuelOrf=0.75, dropCorrOx=0.33, dropCorrFuel=0.33,
                     DorfMin=0.008,
                     LfanOvDorfOx=20.0, LfanOvDorfFuel=20.0)

        R = RocketThruster(name='Shuttle OMS',coreObj=C, injObj=I)
        
        etaMix = effObj('Mix')
        if etaMix > EFF_MIN:
            effMixL.append( etaMix )
            lchamL.append( LchamberInp )
        
    curve = Curve(plot_type='plot', xL=lchamL, yL=effMixL, marker='',
                  label='%g elem/sqin'%elemDensInp,
                  place_labels_on_line=True, xpos_label=xposL[ie],  dy_placement='-7%', dangle_placement=dangL[ie])
                  
    curveL.append( curve )
        

chart = F.add_chart( row=0, col=0, curveL=curveL, 
                     xlabel='Chamber Length (in)', 
                     ylabel='Mixing Efficiency',
                     show_legend=True, legend_loc='lower right',
                     xmin=2, ymin=EFF_MIN, xmax=10, ymax=1.0)
F.make( do_show=True )
