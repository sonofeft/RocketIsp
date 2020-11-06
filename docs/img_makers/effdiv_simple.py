import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

from plothelp.plot_help import Figure, sample_data, Curve, CWheel
from prop_comb_etadiv_data import prop_combD, propcomboL, pcbL
from rocketisp.efficiency.eff_divergence import eff_div
import numpy as np
epsArr = np.linspace(2.8, 200, 100)

propcomboL.sort()
pcbL = pcbL[1:]

MARKERL = ['o','v','^','<','>','d','X','P','s','p','*','.']
CWheel.set_wheel( 'tab10' )

F = Figure( figsize=(7,5), dpi=300, nrows=1, ncols=1,
            sharex=False, sharey=False, hspace=None, wspace=None,
            title='Divergence Efficiency\n(for various propellant combinations)', 
            show_grid=True, tight_layout=True,
            png_path_name= os.path.join(up_one, '_static', 'effdiv_simple.png') )

F.set_x_number_format(major_fmt='g', major_size=10, minor_fmt='g', minor_size=8)
F.set_y_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)

curveL = []

for j,pcb in enumerate(pcbL):
    for i,propcombo in enumerate(propcomboL):
        epsL, effdivL = prop_combD[ (pcb, propcombo) ]
        
        curve = Curve(plot_type='semilogx', xL=epsL, yL=effdivL, marker=MARKERL[i],
                      markerfacecolor=CWheel(j), 
                      label='', linecolor=CWheel(j), linestyle='', linewidth=0)
        curveL.append( curve )

for i,propcombo in enumerate(propcomboL):
    epsL, effdivL = prop_combD[ (pcb, propcombo) ]
    
    curve = Curve(plot_type='semilogx', xL=[.1,.2], yL=[.1,.2], marker=MARKERL[i],
                  markerfacecolor='gray', 
                  label=propcombo, linecolor='gray', linestyle='', linewidth=0)
    curveL.append( curve )


dypL = ['3%','3%','3%','3%','3%','3%']
for j,pcb in enumerate(pcbL):
    effL = [eff_div( eps=eps, pcBell=pcb) for eps in epsArr]
    
    curve = Curve(plot_type='semilogx', xL=epsArr, yL=effL, marker='',
                  place_labels_on_line=True, xpos_label=5, dy_placement=dypL[j],
                  label='%g%%'%pcb, linecolor=CWheel(j), linestyle='', linewidth=1)
    curveL.append( curve )
        
curve.add_extra_text(label='% Bell', xpos_label=5, show_label_frame=False,
                     ypos_label=0.943, dangle_placement=0,
                     alpha=1, alpha_label=1, label_color='#333333')



chart = F.add_chart( row=0, col=0, curveL=curveL, 
                     xlabel='Area Ratio', 
                     ylabel='Divergence Efficiency',
                     show_legend=True, legend_loc='lower right',
                     xmin=2.5, ymin=.94, xmax=200, ymax=1.0)
              


F.make( do_show=True )
