import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

from plothelp.plot_help import Figure, sample_data, Curve, CWheel, plt
from rocketisp.efficiency.calc_full_pcentLossDiv import calc_pcentLossDiv
from rocketisp.efficiency.eff_divergence import eff_div
import numpy as np
from numpy import log
from mlp_example_predict import calc_black_box

fvacL = [5.0]
while fvacL[-1] < 300000.0:
    fvacL.append( 1.2 * fvacL[-1] )
epsL = [3,4,10,20,40,60,80]
pcL = [100, 1000]

CWheel.set_wheel( 'tab10' )

def eles_effbl( Pc=100.0, Fvac=1000.0, eps=20.0):
    """
    Return effBL from ELES boundary layer correlation.
    where: Pc=psia, Fvac=lbf, eps=dimensionless
    """
    logPF   = log(0.01*Pc*Fvac)
    effBL = 0.997 - (log(eps) * 0.01 * (1-0.065*logPF + 0.001*logPF**2))
    return effBL

for Pc in pcL:

    F = Figure( figsize=(5,4), dpi=300, nrows=1, ncols=1,
                sharex=False, sharey=False, hspace=None, wspace=None,
                title='Black Box Value, Pc=%g psia\n(for MLP Model)'%Pc, 
                show_grid=True, tight_layout=True,
                png_path_name= os.path.join(up_one, '_static', 'mlp_example_Pc=%i.png'%Pc ) )

    F.set_x_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8, pad=8)
    F.set_y_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)

    curveL = []

    dyL = ['3%','3%','3%','3%','3%','3%','-3%']
    for j,eps in enumerate(epsL):
        # first plot MLP fit
        effL = [calc_black_box( Pc=Pc, Fvac=Fvac, eps=eps) for Fvac in fvacL]
            
        curve = Curve(plot_type='semilogx', xL=fvacL, yL=effL, marker='',
                      place_labels_on_line=True, xpos_label=100, dy_placement=dyL[j],
                      label='%g:1'%eps, linecolor=CWheel(j), 
                      linestyle='--', linewidth=3)
        curveL.append( curve )
        
        # then plot original data
        effL = [eles_effbl( Pc=Pc, Fvac=Fvac, eps=eps) for Fvac in fvacL]
            
        curve = Curve(plot_type='semilogx', xL=fvacL, yL=effL, marker='',
                      place_labels_on_line=True, xpos_label=100, dy_placement=dyL[j],
                      label='', linecolor='k', 
                      linestyle='-', linewidth=1)
        curveL.append( curve )
            
    msg = 'black lines = original data\ncolored lines = MLP fit'
    curve.add_extra_text(label=msg, xpos_label=10000, ypos_label=0.965, show_label_frame=True,
                         dx_placement=0, dy_placement=0, dangle_placement=0, abs_angle=0,
                         alpha=1, alpha_label=1, label_color='k', label_font_size=12)

    chart = F.add_chart( row=0, col=0, curveL=curveL, 
                         xlabel='Vacuum Thrust (lbf)', 
                         ylabel='Black Box Value',
                         show_legend=True, legend_loc='lower right',
                         xmin=5, ymin=.96, xmax=300000, ymax=1.0)
                  


    F.make( do_show=False )


plt.show()