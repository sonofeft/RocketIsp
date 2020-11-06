import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

import numpy as np
from plothelp.plot_help import Figure, sample_data, Curve, CWheel, plt
from odkspecies.odk_species import ODK_Species

oxName = 'LOX'
fuelName = 'LH2'
Rthrt = 1.0 # inch
Pc = 100 # psia
eps = 20 
pcentBell = 80
MR = 6.0

RthrtL = [0.1, 1, 10]
sL = [] # list of ODK_Species objects
for Rthrt in RthrtL:

    S = ODK_Species(oxName=oxName, fuelName=fuelName,
                    Pc=Pc, Rthrt=Rthrt , eps=eps , MR=MR , pcentBell=pcentBell, 
                    RWTU=1.0, RWTD=1.0, useDBruns=1)
    sL.append(S)

epsL = S.objDB.ode_epsL[1:]

ypos_eqD =   {'H2O':'-3%'}
ypos_frozD = {'OH':'-3%'}

ypos_kinD = {'OH':['4%','-3%','-4%']}
xpos_kinD = {'OH':[0.3*eps, 0.3*eps, 0.35*eps]}

for sp in S.objDB.odksumm.speciesSet:
    if max(S.objDB.odk_speciesDL[sp])>0.05 and max(S.objDB.ode_speciesDL[sp])>0.05:
        curveL = []

        title = 'HO group: %s/%s %s Mass Fraction\n'%(oxName, fuelName, sp) +\
                'MR=%g, Pc=%g psia, AR=%g:1, %%Bell=%g'%(MR, Pc, eps, pcentBell)

        F = Figure( figsize=(5,4), dpi=300, nrows=1, ncols=1,
                    sharex=False, sharey=False, hspace=None, wspace=None,
                    title=title, show_grid=True, tight_layout=True,
                    png_path_name= os.path.join(up_one, '_static', 'ho_%s_%s_%s.png'%(oxName, fuelName, sp)))

        yL = S.objDB.ode_speciesDL[sp][1:]
        dyp = ypos_eqD.get(sp, '3%')
        curve = Curve(plot_type='plot', xL=epsL, yL=yL, marker='',linestyle='--',
                      label='%s equil'%sp, linewidth=1, dy_placement=dyp, linecolor='k',
                      place_labels_on_line=True, xpos_label=0.9*eps)              
        curveL.append( curve )
        
        yL = [S.objDB.odf_speciesD[sp]]*len(epsL)
        dyp = ypos_frozD.get(sp, '3%')
        curve = Curve(plot_type='plot', xL=epsL, yL=yL, marker='',linestyle='--',
                      label='%s frozen'%sp, linewidth=1, dy_placement=dyp, linecolor='k',
                      place_labels_on_line=True, xpos_label=0.9*eps)              
        curveL.append( curve )
        
        for isp,S in enumerate(sL):
            yL = S.objDB.odk_speciesDL[sp][1:]
            dyp = ypos_kinD.get(sp, ['3%','3%','3%'])[isp]
            xp = xpos_kinD.get(sp, [0.5*eps, 0.5*eps, 0.5*eps])[isp]
            curve = Curve(plot_type='plot', xL=epsL, yL=yL, marker='',linestyle='-',
                          label='%s Rt=%g in'%(sp,RthrtL[isp]), linewidth=1, dy_placement=dyp, linecolor=CWheel(isp),
                          place_labels_on_line=True, xpos_label=xp)              
            curveL.append( curve )

        chart = F.add_chart( row=0, col=0, curveL=curveL, 
                             xlabel='Area Ratio', 
                             ylabel='%s Mass Fraction'%sp,
                             show_legend=True, legend_loc='lower right')
                      


        F.make( do_show=False )
    
plt.show()