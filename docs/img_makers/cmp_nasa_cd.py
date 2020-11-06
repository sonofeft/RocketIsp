import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

import numpy as np
from plothelp.plot_help import Figure, sample_data, Curve
from rocketisp.nozzle.cd_throat import get_Cd
from rocketisp.nozzle.cd_throat_NASA8120 import cd_nasa_8120
from rocketisp.nozzle.Cd_NASA_33_548 import cd_nasa_1973

Rup8120Arr = np.linspace(1, 3.6, 50)
cd_8120L = [ cd_nasa_8120( Rup ) for Rup in Rup8120Arr ]

Rup1973Arr = np.linspace(0.4, 2.0, 50)
cd_1973L = [ cd_nasa_1973( Rup ) for Rup in Rup1973Arr ]

curve8120 = Curve(plot_type='line', xL=Rup8120Arr, yL=cd_8120L, marker='',
              label='NASA SP8120', linewidth=3, linecolor='k',
              place_labels_on_line=False, xpos_label=1, dangle_placement=0)

curve1973 = Curve(plot_type='line', xL=Rup1973Arr, yL=cd_1973L, marker='', alpha=0.7,
              label='NASA 33-548 Kliegel', linewidth=3, linecolor='gray', linestyle='--',
              place_labels_on_line=False, xpos_label=1, dangle_placement=0)

F = Figure( figsize=(5,4), dpi=300, nrows=1, ncols=1,
            sharex=False, sharey=False, hspace=None, wspace=None,
            title='Discharge Coefficient (Cd)', show_grid=True, tight_layout=True,
            png_path_name= os.path.join(up_one, '_static', 'cmp_nasa_cd.png') )

F.set_x_number_format(major_fmt='.1f', major_size=10, minor_fmt='', minor_size=8)
F.set_y_number_format(major_fmt='.3f', major_size=10, minor_fmt='', minor_size=8)

curveL = [curve8120, curve1973]
RupArr = np.linspace(.8, 3, 50)
for gamma in [1.4, 1.3, 1.2]:

    cdL = [ get_Cd( Rup=Rup, gamma=gamma ) for Rup in RupArr]
    
    curve = Curve(plot_type='line', xL=RupArr, yL=cdL, marker='', alpha=0.9,
                  label='Const gam=%g'%gamma, linewidth=3, linecolor='',
                  place_labels_on_line=False, xpos_label=0, dangle_placement=0)
                  
    curveL.append( curve )
    

chart = F.add_chart( row=0, col=0, curveL=curveL, 
                     xlabel='Upstream Radius Ratio (RupThroat)', 
                     ylabel='Discharge Coefficient (Cd)',
                     show_legend=True, legend_loc='lower right',
                     ymin=0.985, ymax=1, xmin=0.5, xmax=3.5)
              


F.make( do_show=True )