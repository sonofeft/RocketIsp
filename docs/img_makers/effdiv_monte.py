import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

from plothelp.plot_help import Figure, sample_data, Curve, CWheel
from rocketisp.efficiency.calc_full_pcentLossDiv import calc_pcentLossDiv
from rocketisp.efficiency.eff_divergence import eff_div
import numpy as np
epsArr = np.linspace(2.8, 200, 100)
pcbL = [100,  80, 70]

CWheel.set_wheel( 'tab10' )

F = Figure( figsize=(5,4), dpi=300, nrows=1, ncols=1,
            sharex=False, sharey=False, hspace=None, wspace=None,
            title='Divergence Efficiency\n(for MLP Model)', 
            show_grid=True, tight_layout=True,
            png_path_name= os.path.join(up_one, '_static', 'effdiv_monte_Rd.png') )

F.set_x_number_format(major_fmt='g', major_size=10, minor_fmt='g', minor_size=8, pad=8)
F.set_y_number_format(major_fmt='.2f', major_size=10, minor_fmt='', minor_size=8)

curveL = []
'''
for j,pcb in enumerate(pcbL):
    effL = [eff_div( eps=eps, pcBell=pcb) for eps in epsArr]
    
    curve = Curve(plot_type='semilogx', xL=epsArr, yL=effL, marker='',
                  place_labels_on_line=False, xpos_label=10, dy_placement='3%', alpha=0.25,
                  label='%g%% Bell'%pcb, linecolor=CWheel(j), linestyle='--', linewidth=3)

    curve.add_extra_text(xpos_label=10, dy_placement='3%', label='%g%% Bell'%pcb)
                  
                  
    curveL.append( curve )
'''

dypLL = [['3%','-3%','-3%'],['3%','-3%','3%'],['5%','-4%','-4%']]
for j,pcb in enumerate(pcbL):
    for i,RWTD in enumerate([0.5, 1.0, 2.0]):
        effL = []
        for eps in epsArr:
            eff = (100-calc_pcentLossDiv( Pc=500.0, eps=eps, Rthrt=1.0, pcentBell=pcb, gammaInit=1.2,
                           TcCham=5500.0, MolWt=20.0, RWTD=RWTD )) / 100.0
            effL.append( eff )
            
        curve = Curve(plot_type='semilogx', xL=epsArr, yL=effL, marker='',
                      place_labels_on_line=True, xpos_label=3.5+i, dy_placement=dypLL[j][i],
                      label='Rd=%g'%RWTD, linecolor=CWheel(j), linestyle='', linewidth=i+1)
        curveL.append( curve )
        
        if i==2:
            
            curve.add_extra_text(xpos_label=15, dy_placement=['-3%', '-3%', '-4%'][j], 
                                 label='%g%% Bell'%pcb)
        
msg = 'Rd = Downstream radius \nof curvature ratio'
curve.add_extra_text(label=msg, xpos_label=30, ypos_label=0.95, show_label_frame=True,
                     dx_placement=0, dy_placement=0, dangle_placement=0, abs_angle=0,
                     alpha=1, alpha_label=1, label_color='k', label_font_size=12)


chart = F.add_chart( row=0, col=0, curveL=curveL, 
                     xlabel='Area Ratio', 
                     ylabel='Divergence Efficiency',
                     show_legend=True, legend_loc='lower right',
                     xmin=2.5, ymin=.94, xmax=200, ymax=1.0)
              


F.make( do_show=True )
