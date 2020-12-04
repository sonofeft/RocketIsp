import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

from rocketisp.geometry import Geometry
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream
from rocketisp.injector import Injector
from rocketisp.rocket_isp import RocketThruster
from rocketisp.mr_range import MRrange
from rocketisp.goldSearch import search_max
from rocketcea.biprop_utils.InterpProp_scipy import InterpProp

import numpy as np
from plothelp.plot_help import Figure, sample_data, Curve, plt
from plothelp.plot_help import CWheel

geomObj = Geometry(Rthrt=1,
                   CR=2.5, eps=20.0,  pcentBell=80, 
                   RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                   LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
                   
effObj = Efficiencies(Vap=0.99, Mix=0.99)

# It's an ablative chamber, so some FFC (fuel film cooling) is required... guess about 10%
C = CoreStream( geomObj=geomObj, effObj=effObj, pcentFFC=0.0, Pamb=0.0,
                oxName='N2O4', fuelName='MMH',  MRcore=1.9, Pc=500 )
                
mrr = MRrange(C.ceaObj, Pc=C.Pc, eps=geomObj.eps,
              edge_frac=0.97)
mrlo, mrhi = mrr.get_mr_range()
print('mrlo, mrhi',mrlo, mrhi)
mrcoreL  = np.linspace(mrlo, mrhi, 50) # array of MRcore  (core stream tube mixture ratio)


F = Figure( figsize=(5,4), dpi=300, nrows=1, ncols=1,
            sharex=False, sharey=False, hspace=None, wspace=None,
            title='Em Efficiency\nImpact on Optimum MR', 
            show_grid=True, tight_layout=True,
            png_path_name= os.path.join(up_one, '_static', 'effEm_Isp_impact.png') )

F.set_x_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)
F.set_y_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)

curveL = []

ispD = {} # key=isp type, value= ispL

for elemEm in [0.9, 0.8, 0.7]:
    I   = Injector(C, Tox=None, Tfuel=None, elemEm=elemEm,
                   fdPinjOx=0.25, fdPinjFuel=0.25,
                   elemDensInp=None, NelementsInp=None,
                   setNelementsBy='acoustics', # can be "acoustics", "density", "input"
                   setAcousticFreqBy='mode', # can be "mode" or "freq"
                   #desAcousMode=0.8*4.2012, desFreqInp=2000,
                   desAcousMode='1T',
                   OxOrfPerEl=1.0, FuelOrfPerEl=1.0, 
                   lolFuelElem=True, 
                   CdOxOrf=0.75, CdFuelOrf=0.75, dropCorrOx=1, dropCorrFuel=1,
                   DorfMin=0.008,
                   LfanOvDorfOx=20.0, LfanOvDorfFuel=20.0)


    R = RocketThruster(name='Sample Thruster',coreObj=C, injObj=I, pulse_sec=float('inf'), pulse_quality=0.8)
    R.set_mr_to_max_ispdel()

    ispodeL  = [] # list of IspODE  (one-dimensional equilibrium)
    ispodkL  = [] # list of IspODK  (one-dimensional kinetic)
    ispdelL = [] # list of Isp thruster delivered


    MRsave = C.MRcore

    for mr in mrcoreL:
        R.coreObj.reset_attr( 'MRcore', mr, re_evaluate=True)
        R.calc_all_eff()

        ispodeL.append( R.coreObj.IspODE )
        ispodkL.append( R.coreObj.IspODK )
        ispdelL.append( R.coreObj.IspDel )
        
    R.coreObj.reset_attr( 'MRcore', MRsave, re_evaluate=True)
    R.calc_all_eff()
    
    ispD['ODE'] = ispodeL
    ispD['ODK'] = ispodkL
    ispD[elemEm] = ispdelL
    

# ODE Curve
mr_ode_terp = InterpProp(mrcoreL, ispodeL)
mr_ode_Peak, isp_ode_peak = search_max(mr_ode_terp, mrlo, mrhi, tol=1.0e-5)

curve = Curve(plot_type='plot', xL=mrcoreL, yL=ispodeL, marker='',
              label='IspODE', linecolor=CWheel(0),
              place_labels_on_line=True, xpos_label=mr_ode_Peak,  dy_placement='3%')
              
curveL.append( curve )
    
curve = Curve(plot_type='plot', xL=[mr_ode_Peak, mr_ode_Peak+0.00001], yL=[isp_ode_peak-10, isp_ode_peak], marker='',
              label='', linewidth=1, dy_placement='3%', linecolor=CWheel(0), linestyle='--')              
curveL.append( curve )

# ODK Curve
mr_odk_terp = InterpProp(mrcoreL, ispodkL)
mr_odk_Peak, isp_odk_peak = search_max(mr_odk_terp, mrlo, mrhi, tol=1.0e-5)

curve = Curve(plot_type='plot', xL=mrcoreL, yL=ispodkL, marker='',
              label='IspODK', linecolor=CWheel(1),
              place_labels_on_line=True, xpos_label=mr_odk_Peak,  dy_placement='3%')
              
curveL.append( curve )
    
curve = Curve(plot_type='plot', xL=[mr_odk_Peak, mr_odk_Peak+0.00001], yL=[isp_odk_peak-10, isp_odk_peak], marker='',
              label='', linewidth=1, dy_placement='3%', linecolor=CWheel(1), linestyle='--')              
curveL.append( curve )

for ie,elemEm in enumerate([0.9, 0.8, 0.7]):
    # Delivered Curve
    ispdelL = ispD[elemEm]
    mr_del_terp = InterpProp(mrcoreL, ispdelL)
    mr_del_Peak, isp_del_peak = search_max(mr_del_terp, mrlo, mrhi, tol=1.0e-5)

    curve = Curve(plot_type='plot', xL=mrcoreL, yL=ispdelL, marker='',
                  label='Em=%g'%elemEm, linecolor=CWheel(ie+2),
                  place_labels_on_line=True, xpos_label=mr_del_Peak,  dy_placement='3%')
                  
    curveL.append( curve )
    
    curve = Curve(plot_type='plot', xL=[mr_del_Peak, mr_del_Peak+0.00001], yL=[isp_del_peak-10, isp_del_peak], marker='',
                  label='', linewidth=1, dy_placement='3%', linecolor=CWheel(ie+2), linestyle='--')              
    curveL.append( curve )
        

# build overall chart
chart = F.add_chart( row=0, col=0, curveL=curveL, 
                     xlabel='Mixture Ratio', 
                     ylabel='Isp (sec)',
                     show_legend=False, legend_loc='lower right',
                     ymin=290, ymax=331,
                     xmin=1.5, xmax=2.8)
                     
F.make( do_show=True )
