from math import log10
from scipy.interpolate import interp1d

"""
Digitized data from running 6 common propellant combinations
with given eps, %Bell with the NCO option to find optimum entrance
and exit angles for parabolic nozzle..
"""

def getOptEntranceExitAngles(eps=20.0, pcentBell=80.0):
    """
    Return the entrance and exit angles of an optimum parabolic nozzle
    based on running optimum parabolic nozzle for 6 common propellant combinations
    """
   
    return calcOptEntrance(eps=eps, pcentBell=pcentBell),\
           calcOptExit(eps=eps, pcentBell=pcentBell)
   
   
def calcOptExit(eps=20.0, pcentBell=80.0):
    """
    Return the exit angle of an optimum parabolic nozzle
    based on running optimum parabolic nozzle for 6 common propellant combinations
    """
    
    exit_vs_pcbL = []
            
    leps = log10(eps)
    for i in range( len(pcentBellL) ):
        exit_vs_pcbL.append( my_interp( leps, log10_epsL, exitAngLL[i] ) )

    exitAng = my_interp( pcentBell, pcentBellL, exit_vs_pcbL )
    
    return float(exitAng)
   

def calcOptEntrance(eps=20.0, pcentBell=80.0):
    """
    Return the entrance angle of an optimum parabolic nozzle
    based on running optimum parabolic nozzle for 6 common propellant combinations
    """

    entrance_vs_pcbL = []
    
    leps = log10(eps)
    for i in range( len(pcentBellL) ):
        entrance_vs_pcbL.append( my_interp( leps, log10_epsL, entranceAngLL[i] ) )

    entranceAng = my_interp( pcentBell, pcentBellL, entrance_vs_pcbL )
    
    return float(entranceAng)

pcentBellL = [60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0]
epsL       = [2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 32.0, 64.0, 128.0, 254.0, 512.0]
log10_epsL = [log10(e) for e in epsL]

# ================== ENTRANCE ANGLE ===================
entranceAngLL = []  # list of entrance angle lists

# entrance angle for %Bell = 60
entranceAngLL.append( [29.973723100674352, 30.703527150925463, 31.375401599713616, 32.50168282698206, 33.40406848557244, 34.78364714156141, 35.81495636184458, 38.3632978321238, 40.804325500003884, 42.8932719690786, 44.37273243951821, 45.03585172518701] )
# entrance angle for %Bell = 70
entranceAngLL.append( [24.889319168581522, 26.54643167499322, 27.697917035068816, 29.283465733942116, 30.379886740064197, 31.881781550507643, 32.91456015377038, 35.2812691463901, 37.45934558812611, 39.42812134918116, 41.148616154160855, 42.65509831005929] )
# entrance angle for %Bell = 80
entranceAngLL.append( [21.67031868493122, 23.684957616942242, 25.03567747255991, 26.83410293244355, 28.038936049352028, 29.64234336183151, 30.716328062245793, 33.1040871581794, 35.238446984091034, 37.15564118691893, 38.87313477656137, 40.48346731107629] )
# entrance angle for %Bell = 90
entranceAngLL.append( [19.742711887288984, 21.786336937575935, 23.172252808287908, 25.035451097856498, 26.293548107924085, 27.97687202642521, 29.10754210254295, 31.61517910848991, 33.81740344211038, 35.715159419749796, 37.29304642623832, 38.60104357246711] )
# entrance angle for %Bell = 100
entranceAngLL.append( [18.5324890132203, 20.517801597697712, 21.891212938353807, 23.76936690555109, 25.05605461026849, 26.79690699518092, 27.975484289933963, 30.59797223831989, 32.87198871639589, 34.74600398513161, 36.15510922271028, 37.087911938460756] )
# entrance angle for %Bell = 110
entranceAngLL.append( [17.465640300290687, 19.546583558110974, 20.976127758858645, 22.917707030897436, 24.23878725087337, 26.013987718990798, 27.207436639690975, 29.835893788667576, 32.07797656115928, 33.88750282052223, 35.2060812854958, 36.024157253286305] )

# entrance angle for %Bell = 120 (hand modified to be offset of %Bell==110)
entranceAngLL.append( [16.715640300290687, 18.796583558110974, 20.226127758858645, 22.167707030897436, 23.48878725087337, 25.263987718990798, 26.457436639690975, 29.085893788667576, 31.327976561159282, 33.13750282052223, 34.4560812854958, 35.274157253286305] )

# ================== EXIT ANGLE ===================
exitAngLL = []  # list of entrance angle lists

# exit angle for %Bell = 60
exitAngLL.append( [29.51033948670469, 24.9778346616913, 22.438078468120185, 19.6598392601876, 18.161197995292735, 16.563431324180044, 15.698792318616968, 14.06995568848753, 
                   12.293782355299063,   11.5564, 10.8084, 10.8084] ) # hand modified
                   #12.293782355299063, 12.293782355299063, 12.293782355299063, 12.293782355299063] )

# exit angle for %Bell = 70
exitAngLL.append( [23.4944100788321, 20.257475260652004, 18.311709603284186, 16.015144412462337, 14.671186848171375, 13.130653765700217, 12.25771474333052, 10.756166218598478, 9.851414203812096, 9.851414203812096, 9.851414203812096, 9.851414203812096] )
# exit angle for %Bell = 80
exitAngLL.append( [19.497736426680767, 16.627703731556288, 14.874941728378158, 12.77909988021285, 11.541905418642408, 10.1251759982992, 9.336089866394845, 8.0949574405568, 7.655970510049611, 7.655970510049611, 7.655970510049611, 7.655970510049611] )
# exit angle for %Bell = 90
exitAngLL.append( [16.884559760991653, 13.826846841913325, 12.029574647254673, 9.970673036233617, 8.814398889313027, 7.563557983552768, 6.912942177854027, 5.9991142035649885, 5.746824657133231, 5.746824657133231, 5.746824657133231, 5.746824657133231] )
# exit angle for %Bell = 100
exitAngLL.append( [15.019121312505689, 11.59323135923227, 9.677408163766264, 7.608831253319123, 6.5297124427904185, 5.462359683036683, 4.96729616775217, 4.381421356825546, 4.163350028184571, 4.163350028184571, 4.163350028184571, 4.163350028184571] )
# exit angle for %Bell = 110
exitAngLL.append( [13.26566231196382, 9.665184051022285, 7.720242081765482, 5.712541904263839, 4.728891261681773, 3.838141058326721, 3.4781763261333722, 3.1546637495409677, 2.9449200063252485, 2.9449200063252485, 2.9449200063252485, 2.9449200063252485] )
# exit angle for %Bell = 120
exitAngLL.append( [10.988423990106986, 7.781031684792526, 6.059876205104874, 4.300772361862246, 3.452980528594279, 2.707462070998648, 2.4246071430417278, 2.2316262309137516, 2.1309079746768824, 2.1309079746768824, 2.1309079746768824, 2.1309079746768824] )


def my_interp( xval, xL, yL ):

    if xval < xL[0]:
        return yL[0]
    if xval > xL[-1]:
        return yL[-1]
    
    return interp1d( xL , yL, kind=2, fill_value="extrapolate")(xval)
    
    # ??? fill_value with tuple crashed ???
    #     return interp1d( xL , yL, kind=2, fill_value=(yL[0], yL[-1]))(xval)


if __name__ == "__main__":
    
    import matplotlib.pyplot as plt
    import sys

    do_show = True
    if len(sys.argv) > 1:
        if sys.argv[1] == 'suppress_show':
            do_show = False

    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
    colorL = [c for c in colors]

    fig, ax = plt.subplots()

    epsL = [float(i) for i in range(5, 51, 1)]

    # ======================= ENTRANCE ANGLE =====================
    for ipc,pcb in enumerate([60., 70., 80., 90., 100.]):
        entAngSixL = []
        for eps in epsL:
            (entAng, exitAng) = getOptEntranceExitAngles(eps=eps, pcentBell=pcb)
            entAngSixL.append( entAng )

        ax.plot(epsL, entAngSixL,'-',  linewidth=4, alpha=0.9, color=colorL[ipc], label='%g%% Bell'%pcb )

    plt.legend()
    #plt.ylim(15, 40)
    plt.xlim(0, 50)
    plt.grid()
    plt.title('Skewed Parabola Entrance Angle')
    plt.ylabel('Entrance Angle (deg)')
    plt.xlabel('Area Ratio')
    #plt.text(20,22, 'Huzel = black\n6-Prop = dotted')

    if do_show:
        plt.savefig( 'parabolic_entrance.png' )

    # ===================== EXIT ANGLE ============================
    fig, ax = plt.subplots()

    for ipc,pcb in enumerate([60., 70., 80., 90., 100.]):
        extAngSixL = []
        for eps in epsL:
            (entAng, exitAng) = getOptEntranceExitAngles(eps=eps, pcentBell=pcb)
            extAngSixL.append( exitAng )

        ax.plot(epsL, extAngSixL,'-',  linewidth=4, alpha=0.9, color=colorL[ipc], label='%g%% Bell'%pcb )

    plt.legend()
    #plt.ylim(15, 40)
    plt.xlim(0, 50)
    plt.grid()
    plt.title('Skewed Parabola Exit Angle')
    plt.ylabel('Exit Angle (deg)')
    plt.xlabel('Area Ratio')
    #plt.text(18,18, 'Huzel = black\n6-Prop = dotted')

    if do_show:
        plt.savefig( 'parabolic_exit.png' )

        plt.show()
