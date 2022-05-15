
"""
Rough Curve Fit of Pulsing Efficiency from a few historical liquid engines.
"""


def eff_pulse( pulse_sec=0.1, pulse_quality=0.8):
    """
    VERY ROUGH Guestimate of pulsing efficiency
    (Use as place-holder until test data becomes available)
    """        
    best_eff  = 100. - 0.1415451671778462/pulse_sec  - 0.3648849301597481/(pulse_sec**0.5)
    worst_eff = 100. - 0.027250694282230977/pulse_sec - 4.331742005085193/(pulse_sec**0.5)
    
    # Use as place-holder until test data becomes available.
    return (worst_eff + pulse_quality * (best_eff - worst_eff)) / 100.0


if __name__ == "__main__": #Self Test
    from pylab import *
    import sys

    do_show = True
    if len(sys.argv) > 1:
        if sys.argv[1] == 'suppress_show':
            do_show = False

    fig, ax = subplots()
    
    for pulse_quality in [1, .75, .5, .25, 0.]:
    
        pw = 0.01
        pwL = []
        effL = []
        while pw < 10.0:
            pwL.append( pw )

            effL.append( eff_pulse(pulse_sec=pw, pulse_quality=pulse_quality) )
            pw *= 1.1
        semilogx( pwL, effL, label='pulse_quality=%g'%pulse_quality )

    legend()
    grid( True )
    title('Pulsing Efficiency')
    ylabel('Pulsing Efficiency')
    xlabel('Pulse Width (sec)')
    majorFormatter = FormatStrFormatter('%g')
    gca().xaxis.set_major_formatter(majorFormatter)

    if do_show:
        savefig( 'pulse_eff_range.png' )
        show()
