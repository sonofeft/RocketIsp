from math import cos, pi, log
from scipy.interpolate import interp1d
from rocketisp.nozzle.six_opt_parab import calcOptEntrance
from rocketisp.nozzle.nozzle import bell_net_halfAngle

"""
Fit Divergence Efficiency from running 6 common propellant combinations
with given eps, %Bell with the NCO option to find optimum entrance
and exit angles for parabolic nozzle 

For conical nozzle divergence efficiency, use equation from 1st principles.
"""

def eff_div_cone( halfAngleDeg=18.0 ):
    """
    For conical nozzles, a reasonable approximation comes from a half-angle equation.
    (for exact curves, see Powell report at https://ntrs.nasa.gov/citations/19730012958
    figures 5 and 6 page 48)
    """
    # halfAngleDeg = conical nozzle nozzle half angle
    
    return 0.5 + 0.5 * cos( halfAngleDeg*pi/180.0 )

def eff_div_cone_eps_bell( eps=25.0, pcBell=80.0, Rd=1.0):
    """If half angle is unknown, calculate it from eps, pcBell and Rd"""
    theta = calcOptEntrance( eps=eps, pcentBell=pcBell )
    halfAngleDeg = bell_net_halfAngle( Rd=Rd, eps=eps, pcBell=pcBell, theta=theta )
    
    return eff_div_cone( halfAngleDeg=halfAngleDeg )
    
def eff_div_eles(eps=25.0, pcBell=80.0):
    """
    Divergence efficiency equation taken from 
    Expanded Liquid Engine Simulation (ELES) code, 1984
    (a little rough, but not all that bad.)
    """
    ratmlr = pcBell * 1612.1 / (eps + 1009.) / 100.
    
    if eps <= 20.:
        CFX = .945 + .01*log(eps)
    elif eps > 20.:
        CFX = .958 + .00566*log(eps)
    
    effDiv = 1. - (1.-CFX)*((1.75-ratmlr)/.75)**1.7
    return effDiv


def eff_div( eps=25.0, pcBell=80.0):
    """
    Divergence Efficiency from running 6 common propellant combinations
    """
        
    if pcBell<60.0 or pcBell>120.0:
        print('WARNING... Divergence Efficiency %%Bell Range is 60%% to 120%%, %g was input'%pcBell)
        pcBell = max(60, min(120, pcBell))
        print('    ...Looking up Divergence Efficiency Values for %%Bell = %g'%pcBell)
    
    effL = [bf(eps) for bf in pcBellFuncL]
    return interp1d( pcentBellL , effL, kind=2, fill_value="extrapolate")( pcBell )

pcentBellL = [60., 70., 80., 90., 100., 120.]

# curve fits of divergence efficiency for %Bell from 60 to 120 as function of area ratio.
pcBell120 = lambda x: 0.9997896193436784 - 0.00836547101429648/x - 1.8072678278328226e-08/x**.5
pcBell100 = lambda x: 0.9989509055092716 - 0.027302115360697286/x - 2.227978789532209e-08/x**.5
pcBell90 = lambda x: 0.9971299043689117 - 0.03820495281446622/x - 2.591748813286344e-08/x**.5
pcBell80 = lambda x: 0.9941974506864701 - 0.06403015875188575/x - 1.7996764332283723e-08/x**.5
pcBell70 = lambda x: 0.9880774081200867 - 0.09006900924820571/x - 0.00018544403669973342/x**.5
pcBell60 = lambda x: 0.9795420864904427 - 0.0981313348710805/x - 0.02104281165829153/x**.5

pcBellFuncL = [pcBell60, pcBell70, pcBell80, pcBell90, pcBell100, pcBell120]

if __name__ == "__main__": #Self Test
    import pylab
    import sys
    do_show = True
    if len(sys.argv) > 1:
        if sys.argv[1] == 'suppress_show':
            do_show = False
    
    prop_cycle = pylab.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
    colorL = [c for c in colors]
    
    pylab.figure( figsize=(9,7) )
    
    epsL = list( range(3, 301, 1) )
    pcbL = pcentBellL[:]
    pcbL.reverse() # make legend easier to line up with curves
    for i,pcBell in enumerate(pcbL):
        effL = [eff_div(eps=eps, pcBell=pcBell) for eps in epsL]
        pylab.semilogx(epsL, effL, '-', label='%%Bell=%g'%pcBell, color=colorL[i])
        
        
        #effL = [eff_div_eles(eps=eps, pcBell=pcBell) for eps in epsL]
        #pylab.semilogx(epsL, effL, '--', label='', color=colorL[i])
        
        #effL = [eff_div_cone_eps_bell(eps=eps, pcBell=pcBell) for eps in epsL]
        #if i==5:
        #    msg = 'Conical'
        #else:
        #    msg = ''
        #pylab.semilogx(epsL, effL, '--', label=msg, color=colorL[i])
            

    pylab.title('Nozzle Divergence Efficiency')
    pylab.xlabel('Area Ratio')
    pylab.ylabel('Divergence Efficiency')
    pylab.legend()
    pylab.grid(True)
    
    print('eff_div_eles(eps=25.0, pcBell=80.0) =', eff_div_eles(eps=25.0, pcBell=80.0))
    print('eff_div_eles(eps=10.0, pcBell=80.0) =', eff_div_eles(eps=10.0, pcBell=80.0))
    print('eff_div( eps=25.0, pcBell=55.0) =', eff_div( eps=25.0, pcBell=55.0))
    print('eff_div_cone_eps_bell( eps=25.0, pcBell=80.0, Rd=1.0) =', eff_div_cone_eps_bell( eps=25.0, pcBell=80.0, Rd=1.0))
    
    if do_show:
        pylab.savefig( 'div_eff.png' )
        pylab.show()
            
