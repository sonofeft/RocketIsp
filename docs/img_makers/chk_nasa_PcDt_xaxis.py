import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version
import numpy as np
from plothelp.plot_help import Figure, sample_data, Curve, CWheel, plt
from rocketisp.efficiency.effBL_NASA_SP8120 import eff_bl_NASA
from rocketisp.efficiency.calc_full_pcentLossBL import calc_pcentLossBL

# NASA x axis goes from Pc*Dt = 8 to 2000
print('Not a useful graph')
sys.exit()

PcDtL = [250]
while PcDtL[-1] < 2000:
    PcDtL.append( PcDtL[-1]*1.2 )

def make_pc_chart( Rthrt=1, eps=20., pcentBell=80., TcCham=5500. ):
    
    png_path_name = '' #os.path.join(up_one, '_static', 'chk_PcDt_Pcparam_eps%g.png'%eps )
    title = 'Check Pc*Dt as Independent Variable'

    F = Figure( figsize=(6,6), dpi=300, nrows=1, ncols=1,
                sharex=False, sharey=False, hspace=None, wspace=None,
                title=title, show_grid=True, tight_layout=True,
                png_path_name=png_path_name )
                
    F.set_x_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)
    F.set_y_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)

    curveL = []

    for Pc in [100, 200, 500, 1000, 4000]:
        effblL = []
        for PcDt in PcDtL:
            Rthrt = PcDt/Pc/2.0
            effblL.append( (100-calc_pcentLossBL( Pc=Pc, eps=eps, Rthrt=Rthrt, 
                                             pcentBell=pcentBell, TcCham=TcCham ))/100.0 )
        
        curve = Curve(plot_type='semilogx', xL=PcDtL, yL=effblL, marker='',
                      label='Pc=%g psia'%Pc,
                      linestyle='-', linewidth=1, linecolor='',
                      place_labels_on_line=True, dy_placement=0)

        curveL.append( curve )

    chart = F.add_chart( row=0, col=0, curveL=curveL, 
                         xlabel='Pc(psia) * Dt(inch)', 
                         ylabel='Boundary Layer Efficiency',
                         show_legend=True, legend_loc='lower right')
    F.make( do_show=True )
    
    
make_pc_chart( Rthrt=1, eps=20., pcentBell=80., TcCham=5500. )

#plt.show()

