from scipy.interpolate import interp1d

def getHuzelThetaAlpha( eps=20.0, pcBell=80.0 ):
    """For backward compatibility"""
    return getHuzelEntranceExitAngles( eps=eps, pcBell=pcBell )

def getHuzelEntranceExitAngles( eps=20.0, pcBell=80.0 ):
    """
    Return the entrance and exit angle of an optimum parabolic nozzle
    based on the chart from Huzel and Huang.
    """
    
    if eps<5.0 or eps>50.0:
        print('WARNING... Huzel Area Ratio Range is 5 to 50, %g was input'%eps)
        eps = max(5, min(50, eps))
        print('    ...Looking up Huzel Values for Area Ratio = %g'%eps)
        
    if pcBell<60.0 or pcBell>100.0:
        print('WARNING... Huzel %%Bell Range is 60%% to 100%%, %g was input'%pcBell)
        pcBell = max(60, min(100, pcBell))
        print('    ...Looking up Huzel Values for %%Bell = %g'%pcBell)
    
    ent_vs_pcbL = []
    exit_vs_pcbL = []
    
    # using curve fits for smoother result.
    for entFunc in entFuncL:
        ent_vs_pcbL.append( entFunc(eps) )
    
    for exitFunc in exitFuncL:
        exit_vs_pcbL.append( exitFunc(eps) )
    
    entAng = my_interp( pcBell, pcentBellL, ent_vs_pcbL )
    exitAng = my_interp( pcBell, pcentBellL, exit_vs_pcbL )
    
    return float(entAng), float(exitAng)


pcentBellL = [60., 70., 80., 90., 100.]

# curve fits of digitized data
# ================== ENTRANCE ANGLE ==============
entrance60 = lambda x : 37.952183710967816 - 72.82296943108001/x + 116.50935890671563/x**2 + 0.03908728169187725*x
entrance70 = lambda x : 21.740537679637836 + 0.7954309131286522*x - 0.01750181078978021*x**2 + 0.0001373460237589219*x**3
entrance80 = lambda x : 18.979667836126286 + 0.7877832253592264*x - 0.01712226792891003*x**2 + 0.00013290798922516167*x**3
entrance90 = lambda x : 17.50576360467334 + 0.7557447339673545*x - 0.015935763833699292*x**2 + 0.00012055537829958052*x**3
entrance100 = lambda x : 16.98178501000988 + 0.6226046873575315*x - 0.011451858666443436*x**2 + 7.921750330562756e-05*x**3
entFuncL = [entrance60, entrance70, entrance80, entrance90, entrance100]

# ================== EXIT ANGLE ===================
exit60 = lambda x : 11.353312188655671 + 76.98612436768272/x - 164.82552233146757/x**2
exit70 = lambda x : 8.66386177206354 + 70.25682206514529/x - 152.89680675700077/x**2
exit80 = lambda x : 6.8980223189239 + 48.46027742603077/x - 75.14966734642087/x**2
exit90 = lambda x : 1/(0.14065452978211 - 0.2731182505979727/x + 0.00040277870331184107*x)
exit100 = lambda x : 1/(0.19553718885705784 - 0.4196990537300196/x + 0.0005227095915574509*x)
exitFuncL = [exit60, exit70, exit80, exit90, exit100]

# ================== Digitized ENTRANCE ANGLE ==============
entEpsLL = []  # list of entrance angle area ratio lists
entAngLL = []  # list of entrance angle lists

# entrance angle for %Bell = 60
entEpsLL.append( [4.91975, 9.96832, 15.0517, 19.9958, 25.0444, 30.0581, 35.0719, 40.016, 45.0298, 50.1828] )
entAngLL.append( [28.152, 32.2483, 34.1779, 35.3289, 36.2091, 36.8862, 37.3602, 37.8003, 38.1388, 38.4773] )

# entrance angle for %Bell = 70
entEpsLL.append( [5.12865, 10.038, 15.0517, 20.0655, 25.0792, 30.1278, 35.0023, 39.8767, 45.0646, 50.2524] )
entAngLL.append( [25.4098, 28.0165, 30.2509, 31.8082, 32.8576, 33.5685, 33.9409, 34.381, 34.6519, 34.9227] )

# entrance angle for %Bell = 80
entEpsLL.append( [5.05902, 9.9335, 15.0865, 20.1351, 24.9748, 30.0233, 35.0023, 40.0508, 45.0646, 50.1828] )
entAngLL.append( [22.5661, 25.2067, 27.4072, 29.0322, 30.0478, 30.7925, 31.2665, 31.5712, 31.9097, 32.1805] )

# entrance angle for %Bell = 90
entEpsLL.append( [5.12865, 10.1772, 14.9473, 19.961, 25.0444, 30.093, 35.0023, 39.9812, 45.0994, 50.148] )
entAngLL.append( [20.975, 23.6494, 25.6806, 27.2379, 28.3212, 29.0322, 29.6077, 29.9462, 30.3186, 30.4879] )

# entrance angle for %Bell = 100
entEpsLL.append( [5.16347, 10.038, 14.9821, 20.1351, 25.114, 30.0233, 35.0371, 39.9812, 45.0646, 50.148] )
entAngLL.append( [19.8578, 22.2276, 24.0218, 25.5114, 26.5947, 27.4749, 28.1858, 28.6259, 29.066, 29.3707] )

# ================== Digitized EXIT ANGLE ===================
exitEpsLL = []  # list of exit angle area ratio lists
exitAngLL = []  # list of exit angle lists

# exit angle for %Bell = 60
exitEpsLL.append( [4.98025, 10.215, 15.0978, 20.0685, 24.9953, 29.9221, 35.0688, 40.0396, 44.9224, 50.1571] )
exitAngLL.append( [20.1576, 17.3253, 15.8649, 14.7586, 14.0505, 13.6079, 13.2982, 13.1211, 13.0769, 13.0326] )

# exit angle for %Bell = 70
exitEpsLL.append( [5.06823, 10.215, 15.0978, 20.1565, 24.9953, 30.0101, 35.0248, 40.0396, 44.9664, 50.2011] )
exitAngLL.append( [16.573, 14.0505, 12.7229, 11.8378, 11.2182, 10.6872, 10.4659, 10.2004, 10.2446, 10.1561] )

# exit angle for %Bell = 80
exitEpsLL.append( [5.1562, 10.215, 15.1857, 20.0685, 24.9953, 29.9661, 34.9809, 39.9956, 44.8344, 50.2011] )
exitAngLL.append( [13.4752, 10.9084, 9.71356, 9.094, 8.78422, 8.56295, 8.25316, 8.07615, 7.89913, 7.72211] )

# exit angle for %Bell = 90
exitEpsLL.append( [5.06823, 10.083, 15.2297, 20.1125, 24.9953, 30.0101, 35.0248, 39.9516, 44.9224, 50.1571] )
exitAngLL.append( [11.2625, 8.51869, 7.67786, 7.41233, 7.14681, 7.01404, 6.92554, 6.5715, 6.5715, 6.39448] )

# exit angle for %Bell = 100
exitEpsLL.append( [5.11221, 10.083, 15.1417, 20.0685, 24.9953, 29.9221, 35.0688, 39.9076, 44.9224, 50.2451] )
exitAngLL.append( [8.6072, 6.35023, 5.59791, 5.33238, 5.24387, 5.19962, 4.88984, 4.88984, 4.80133, 4.62431] )

def my_interp( xval, xL, yL ):

    if xval < xL[0]:
        return yL[0]
    if xval > xL[-1]:
        return yL[-1]
    
    return interp1d( xL , yL, kind=2, fill_value="extrapolate")(xval)
    

if __name__ == "__main__":
    
    for (eps,pcb) in [(10., 70.),(20.,80.), (40.,90.), (60.,100.), (80.,110.)]:
        
        entAng, exitAng = getHuzelEntranceExitAngles(eps=eps, pcBell=pcb)
        print( 'eps=%6.0f pcentBell=%6.0f  Entrance Angle=%8.4f  Exit Angle=%8.4f'%
               (eps, pcb, entAng, exitAng) )
    
    
    epsL = [float(i) for i in range(5, 51, 5)]
    entL = [float('%4.1f'%getHuzelEntranceExitAngles(eps=eps, pcBell=80.0)[0]) for eps in epsL]
    extL = [float('%4.1f'%getHuzelEntranceExitAngles(eps=eps, pcBell=80.0)[-1]) for eps in epsL]
    print( epsL )
    print( entL )
    print( extL )

