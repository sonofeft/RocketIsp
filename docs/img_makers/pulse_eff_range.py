import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

from plothelp.plot_help import Figure, sample_data, Curve, plt
from rocketisp.efficiency.eff_pulsing import eff_pulse

F = Figure( figsize=(5,4), dpi=300, nrows=1, ncols=1,
            sharex=False, sharey=False, hspace=None, wspace=None,
            title='Pulsing Efficiency', show_grid=True, tight_layout=True,
            png_path_name= os.path.join(up_one, '_static', 'pulse_eff_range.png') )

F.set_x_number_format(major_fmt='g', major_size=10, minor_fmt='', minor_size=8)
F.set_y_number_format(major_fmt='.1f', major_size=10, minor_fmt='', minor_size=8)

curveL = []
for pulse_quality in [1, .75, .5, .25, 0.]:

    pw = 0.01
    pwL = []
    effL = []
    while pw < 10.0:
        pwL.append( pw )

        effL.append( eff_pulse(pulse_sec=pw, pulse_quality=pulse_quality) )
        pw *= 1.1
    
    curve = Curve(plot_type='semilogx', xL=pwL, yL=effL, marker='',
                  label='pulse_quality=%g'%pulse_quality,
                  place_labels_on_line=False, xpos_label=pwL[0], dangle_placement=-45)
                  
    curveL.append( curve )
    

chart = F.add_chart( row=0, col=0, curveL=curveL, 
                     xlabel='Pulse Wdith (sec)', 
                     ylabel='Pulsing Efficiency',
                     show_legend=True, legend_loc='lower right' )
              


F.make( do_show=True )