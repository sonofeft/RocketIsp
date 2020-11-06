import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

from plothelp.plot_help import Figure, sample_data, Curve, plt
import numpy as np
from rocketisp.nozzle.cd_throat import get_Cd
from rocketisp.nozzle.calc_full_Cd import calc_Cd
from rocketcea.cea_obj import CEA_Obj

RupArr = np.linspace(0.75, 3, 50)
cd_simpL = [ get_Cd( Rup=Rup, gamma=1.2 ) for Rup in RupArr ]

rangeD = {} # index=pvar, value=list of pvar values
rangeD['Pc'] = reversed([100, 200, 500, 1000, 3000])
rangeD['Rthrt'] = reversed([.25, .5, 1, 2, 10])
rangeD['Best'] = ['high Pc, big Rthrt']
rangeD['Worst'] = ['low Pc, small Rthrt']

unitsD = {'Pc':'psia', 'Rthrt':'in', 'Best':'', 'Worst':''}

def make_new_chart( pvar='Pc', Pc=200, Rthrt=1 ):
    
    if pvar=='Pc':
        title = '%s Impact on Cd Throat\n(Rthrt=%g inch)'%(pvar, Rthrt)
    elif pvar=='Rthrt':
        title = '%s Impact on Cd Throat\n(Pc=%g psia)'%(pvar, Pc)
    elif pvar in ['Best','Worst']:
        title = 'Cd Throat\n(Pc=%g psia, Rthrt=%g inch)'%(Pc, Rthrt)

    png_path_name = os.path.join(up_one, '_static', 'cmp_cd_calcs_%s.png'%pvar.lower() )

    F = Figure( figsize=(4,4), dpi=300, nrows=1, ncols=1,
                sharex=False, sharey=False, hspace=None, wspace=None,
                title=title, show_grid=True, tight_layout=True,
                png_path_name=png_path_name )

    curve = Curve(plot_type='line', xL=RupArr, yL=cd_simpL, marker='',
                  label='Simple Model',
                  linestyle='--', linewidth=3, linecolor='k',
                  place_labels_on_line=True, dy_placement=0.001)

    curveL = [ curve ]

    chart = F.add_chart( row=0, col=0, curveL=curveL, 
                         xlabel='Upstream Radius Ratio (RupThroat)', 
                         ylabel='Cd',
                         show_legend=True, legend_loc='lower right',
                         ymin=0.975, ymax=1.0)
    
    
    inpD = {'Pc':Pc,  'Rthrt':Rthrt}

    for i, pval in enumerate( rangeD[pvar] ):    
        cd_mlpL = []
        if pvar in ['Best','Worst']:
            pval_str = pval
        else:
            inpD[pvar] = pval
            pval_str = '%g'%pval
        for Rup in RupArr:
            inpD['RWTU'] = Rup
            cd_mlpL.append( calc_Cd(**inpD) )

        if pvar in ['Best','Worst']:
            curve = Curve(plot_type='line', xL=RupArr, yL=cd_mlpL, marker='',
                          label='%s MLP\n%s %s'%(pvar, pval, unitsD[pvar]),
                          place_labels_on_line=True, dy_placement=-0.002)
        else:
            curve = Curve(plot_type='line', xL=RupArr, yL=cd_mlpL, marker='',
                          label='%s=%s %s'%(pvar, pval, unitsD[pvar]))

            if i==4:
                curve.add_extra_text(label='MLP Model', xpos_label=None, show_label_frame=False,
                                     dx_placement=0, dy_placement='-4%', dangle_placement=0,
                                     alpha=1, alpha_label=1)

        chart.add_curve( curve )
        #ax.plot(RupArr, cd_mlpL,'-', color=colorL[i],  label='%s=%s %s'%(pvar, pval, unitsD[pvar]) )
    
    F.make(  )
    

make_new_chart( pvar='Pc' )
make_new_chart( pvar='Rthrt' )
make_new_chart( pvar='Best', Pc=3000, Rthrt=10 )
make_new_chart( pvar='Worst', Pc=100, Rthrt=.25 )

plt.show(  )
