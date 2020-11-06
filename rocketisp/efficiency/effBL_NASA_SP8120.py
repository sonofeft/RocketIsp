

from math import log

# coefficients from curve fit of NASA SP8120 Boundary Layer Loss Recommendation.
a=0.13956490814036465
b=0.4839954048378114
c=-1.5290708783162201
d=1.8872208607881908
e=1.2281287531868839
f=1.1165014352424605
g=0.08873349847277191

def eff_bl_NASA( Dt=1.0, Pc=100, eps=25.0):
    """
    Boundary layer loss correlation Digitized from the NASA SP 8120 document.
    # Dt      throat diameter (in)
    # Pc      chamber pressure (psia)
    # eps     nozzle exit area ratio
    # For each area ratio, the lists are for (Pc*Dt) and % loss due to boundary layer
    #   Pc * Dt is lbf/in^2 * in = lbf/in    
    """
    # MABL is half of NASA correlation
    
    pxd = Pc * Dt # psia * inches
    
    frac = c + d * log(e + eps*f)
    loss = g*eps/pxd + frac/( a + b*log(pxd) )
    
    # turn loss value into an efficiency.
    return (100.0 - loss) / 100.0
    
def regen_corrected_bl( eff_bl=0.98, eps=30., noz_regen_eps=1.0 ):
    """
    Adjust nozzle boundary layer loss for some or all of nozzle regen cooling.
    (assume drag portion of loss is 15 to 30 percent)
    """
    # if no portion of nozzle is regen cooled, simply return eff_bl
    if noz_regen_eps <= 1.0:
        return eff_bl
    
    BLloss = 1.0 - eff_bl
    DragFrac = min(0.3, 0.15 + 0.15 * eps / 200.0) # drag is 30% at eps=200
    DragLoss = DragFrac * BLloss
    EnthLoss = BLloss - DragLoss
    if noz_regen_eps >= eps:
        EnthLoss = 0.0
    else:
        EpsTerm = 1.0 - noz_regen_eps / eps
        EnthLoss = 0.5 * EnthLoss * EpsTerm
    
    eff_bl = 1.0 - DragLoss - EnthLoss
    return eff_bl
    

if __name__ == "__main__": #Self Test
    # plot NASA data and correlation on same chart.
    import pylab
    import sys
    do_show = True
    if len(sys.argv) > 1:
        if sys.argv[1] == 'suppress_show':
            do_show = False
    
    
    pylab.figure( figsize=(9,7) )
    
    nasa_epsL = [3., 5., 10., 20., 40., 60., 80.]

    # the following lists are used by eff_bl_NASA
    # eps = 3
    pxd3L = [7.91256, 9.98901, 13.0916, 18.3392, 25.2661, 34.5208, 49.9948, 72.4052, 99.339, 140.906, 192.518, 251.267, 339.044, 453.694, 654.568, 1013.25, 1939.3]
    pct3L = [1.29734, 1.17043, 1.03445, 0.907531, 0.798746, 0.717158, 0.635569, 0.572111, 0.526784, 0.481457, 0.43613, 0.408934, 0.390803, 0.363607, 0.345476, 0.33641, 0.327345]

    # eps = 5
    pxd5L = [8.04822, 9.98009, 13.3161, 18.3457, 24.3662, 35.6278, 53.5449, 74.1077, 98.4277, 145.243, 206.618, 289.919, 435.719, 625.541, 1016.2, 1937.68]
    pct5L = [1.99111, 1.79167, 1.59223, 1.42271, 1.27313, 1.09364, 0.954028, 0.86428, 0.784505, 0.704729, 0.644897, 0.614981, 0.575094, 0.55515, 0.515262, 0.50529]

    # eps = 10
    pxd10L = [7.7234, 10.0259, 13.6869, 18.6847, 25.5075, 34.3467, 49.5362, 71.7708, 99.3329, 147.251, 221.303, 331.076, 493.039, 698.179, 1016.2, 1928.84]
    pct10L = [3.00825, 2.71906, 2.42988, 2.19055, 1.98114, 1.82159, 1.64209, 1.48254, 1.37285, 1.25319, 1.16344, 1.10361, 1.04378, 0.983944, 0.944056, 0.91414]

    # eps = 20
    pxd20L = [7.93846, 9.98009, 13.1345, 17.4448, 23.4901, 32.9605, 46.6744, 66.7022, 99.3329, 146.579, 219.286, 322.107, 484.094, 730.881, 1020.86, 1937.68]
    pct20L = [4.12511, 3.80601, 3.45699, 3.12791, 2.8487, 2.58943, 2.33016, 2.12075, 1.89139, 1.72187, 1.59223, 1.48254, 1.38282, 1.32299, 1.23324, 1.14349]

    # eps = 40
    pxd40L = [8.01147, 9.98009, 12.7786, 15.9917, 20.6643, 27.0714, 36.2861, 47.5369, 64.8952, 81.9594, 99.3329, 130.729, 179.284, 244.75, 337.194, 460.322, 619.84, 779.252, 1011.56, 1387.27, 1946.57]
    pct40L = [5.17216, 4.70348, 4.28466, 3.96556, 3.62651, 3.31738, 3.05811, 2.82875, 2.62932, 2.47974, 2.37004, 2.23044, 2.09083, 1.98114, 1.87145, 1.80164, 1.72187, 1.68198, 1.63212, 1.58226, 1.51246]

    # eps = 60
    pxd60L = [8.08515, 9.93451, 12.7203, 16.5124, 21.2397, 27.6982, 36.2861, 49.0848, 66.7022, 99.3329, 145.243, 206.618, 296.631, 406.805, 578.709, 779.252, 1011.56, 1362.1, 1946.57]
    pct60L = [6.02975, 5.5511, 5.04253, 4.60376, 4.22483, 3.90573, 3.60657, 3.32735, 3.07805, 2.79884, 2.56948, 2.38002, 2.23044, 2.11077, 2.00108, 1.91134, 1.84153, 1.77173, 1.69195]

    # eps = 80
    pxd80L = [8.04822, 9.93451, 12.7203, 16.8175, 23.0639, 31.9211, 46.0379, 66.0944, 100.247, 146.579, 211.401, 313.381, 449.906, 651.849, 861.813, 1011.56, 1349.69, 1928.84]
    pct80L = [7.14661, 6.37877, 5.72062, 5.15222, 4.62371, 4.18494, 3.78606, 3.44702, 3.11794, 2.85867, 2.64926, 2.45979, 2.2803, 2.14069, 2.04097, 1.99111, 1.91134, 1.81162]

    pxdLL = [pxd3L, pxd5L, pxd10L, pxd20L, pxd40L, pxd60L, pxd80L]
    pctLL = [pct3L, pct5L, pct10L, pct20L, pct40L, pct60L, pct80L]
    
    MARKERL = ['o','v','^','<','>','d','X','P','s','p','*','.']
    COLORL = ['g','c','b','y','#FFA500','m','r']
    
    i = 0
    for area_ratio, pxdL, lossL in zip(nasa_epsL, pxdLL, pctLL):
        effL = [(100.0 - loss) / 100.0  for loss in lossL]
        pylab.semilogx(pxdL, effL, '.', marker=MARKERL[i], color=COLORL[i], label='ref AR=%g'%area_ratio)
        i += 1
        
    i = 0
    for area_ratio, pxdL in zip(nasa_epsL, pxdLL):
        lossL = [eff_bl_NASA( Dt=1.0, Pc=pxd, eps=area_ratio) for pxd in pxdL ]
        
        # show impact of partially regen cooled nozzle
        #lossL = [regen_corrected_bl( eff_bl=eff_bl, eps=area_ratio, noz_regen_eps=6.0 ) for eff_bl in lossL]
        
        pylab.semilogx(pxdL, lossL, '-', color=COLORL[i], label='fit AR=%g'%area_ratio)
        i += 1
        

    pylab.title('Boundary Layer Nozzle Efficiency')
    pylab.xlabel('Pc(psia) * Dt(inch)')
    pylab.ylabel('BL Efficiency')
    pylab.legend()
    
    if do_show:
        pylab.savefig( 'nasa_sp8120_bl_eff.png' )
        
        pylab.show()

