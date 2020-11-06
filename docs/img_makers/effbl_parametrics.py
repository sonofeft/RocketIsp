import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version
import numpy as np
from plothelp.plot_help import Figure, sample_data, Curve, CWheel, plt
from rocketisp.efficiency.effBL_NASA_SP8120 import eff_bl_NASA
from rocketisp.efficiency.calc_full_pcentLossBL import calc_pcentLossBL

# NASA x axis goes from Pc*Dt = 8 to 2000

rtL = [.1]
while rtL[-1] < 10:
    rtL.append( rtL[-1]*1.2 )

epsL = [3,5,10,20,40,80]

def make_pc_chart( Pc=100, pcentBell=80., TcCham=5500. ):
    
    png_path_name = os.path.join(up_one, '_static', 'effbl_parametrics_Pc%g.png'%Pc )
    title = 'Pc = %g psia\nMLP vs NASA SP8120 Boundary Layer Efficiency'%Pc

    F = Figure( figsize=(6,5), dpi=300, nrows=1, ncols=1,
                sharex=False, sharey=False, hspace=None, wspace=None,
                title=title, show_grid=True, tight_layout=True,
                png_path_name=png_path_name )
                
    F.set_x_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)
    F.set_y_number_format(major_fmt='.3f', major_size=10, minor_fmt='', minor_size=8)

    curveL = []

    for i,eps in enumerate(epsL):
        
        # show MLP curves
        effblL = []
        for Rthrt in rtL:
            effblL.append( (100-calc_pcentLossBL( Pc=Pc, eps=eps, Rthrt=Rthrt, 
                                             pcentBell=pcentBell, TcCham=TcCham ))/100.0 )
        curve = Curve(plot_type='semilogx', xL=rtL, yL=effblL, marker='',
                      label='MLP %g:1'%eps, xpos_label=.2,
                      linestyle='-', linewidth=2, linecolor=CWheel(i),
                      place_labels_on_line=True, dy_placement='2%')
        curveL.append( curve )

        
    for i,eps in enumerate(epsL):
        # show NASA curves
        effblL = []
        short_rtL = []
        for Rthrt in rtL:
            DtPc = 2.0*Rthrt*Pc
            if DtPc>=8.0 and DtPc<=2000:
                effblL.append( eff_bl_NASA( Dt=2.0*Rthrt, Pc=Pc, eps=eps)  )
                short_rtL.append( Rthrt )
                
        curve = Curve(plot_type='semilogx', xL=short_rtL, yL=effblL, marker='',
                      label='NASA %g:1'%eps, xpos_label=1,
                      linestyle='--', linewidth=1, linecolor=CWheel(i),
                      place_labels_on_line=True, dy_placement='2%')
        curveL.append( curve )

    msg =  'Area Ratio = 3:1 to 80:1\n'+\
           '%%Bell=%g, Tc=%g degR\n'%( pcentBell, TcCham) +\
           'NASA = NASA Report SP 8120\n'+\
           'MLP = Multi-layer Perceptron Regressor'
           
    curve.add_extra_text(label=msg, xpos_label=3, ypos_label=0.965,
                         show_label_frame=True,
                         dx_placement=0, dy_placement=0, dangle_placement=0, abs_angle=0,
                         alpha=1, alpha_label=1, label_color='k')#, label_font_size=12)


    chart = F.add_chart( row=0, col=0, curveL=curveL, 
                         xlabel='Throat Radius (Rthrt, inch)', 
                         ylabel='Boundary Layer Efficiency',
                         show_legend=True, legend_loc='lower right', ymin=0.96, ymax=1.0)
    F.make( do_show=False )
    
    
make_pc_chart( Pc=100, pcentBell=80., TcCham=5500. )
#make_pc_chart( Pc=200, pcentBell=80., TcCham=5500. )
#make_pc_chart( Pc=500, pcentBell=80., TcCham=5500. )
make_pc_chart( Pc=1000, pcentBell=80., TcCham=5500. )

plt.show()

