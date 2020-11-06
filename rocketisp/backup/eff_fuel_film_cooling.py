

def solveFractionBarrierFlow( pcentFFC=25.0, mrCore=2.5, mrBarrier=1.2):
    """
    Given percent of fuel that goes into barrier, calculate the fraction of
    total flow that goes through barrier (i.e. ox + fuel at mrBarrier)
    """
    ffc = pcentFFC / 100.0
    mrEng = mrCore * (1.0 - ffc)
    
    # let wdotTotal = 1.0
    wdotTotal = 1.0
    wdfEng = wdotTotal / (1.0 + mrEng)
    wdoEng = wdotTotal - wdfEng

    # consider improving by using better root solver.
    # solve for flow split between barrier and core
    fbmin = 0.0
    fbmax = 1.0
    for i in range(40):
        fb = (fbmin + fbmax) / 2.0
        wdb = fb * wdotTotal

        # barrier flows
        wdbFuel = wdb / (1.0 + mrBarrier)
        wdbOx = wdb - wdbFuel

        # core flows
        wdcFuel = wdfEng - wdbFuel
        wdcOx = wdoEng - wdbOx

        if wdcFuel > 0.0:
            mrCoreCalc = wdcOx / wdcFuel
            if mrCoreCalc > mrCore:
                fbmax = fb
            else:
                fbmin = fb
            #print 'mrCoreCalc',mrCoreCalc,' at fb=',fb
        else:
            fbmax = fb

    return (fbmin + fbmax) / 2.0

if __name__ == "__main__": #Self Test
    
    frac_barrier = solveFractionBarrierFlow( pcentFFC=25.0, mrCore=2.5, mrBarrier=1.2)
    print('frac_barrier =',frac_barrier)
    print('         ans =',0.3678929765887915)

