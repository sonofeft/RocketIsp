from scipy.interpolate import interp1d
from math import log

# upstream radius / throat radius
RupL = [ 0.75, 1.0, 1.5, 2.0, 2.5, 3.0]

def get_Cd( Rup=1.5, gamma=1.25 ):
    
    # Rup=0.75,  std=3.85922e-05
    cd_075 =   1/(1.021593870476789 - 0.00639987485225013*gamma)
    # Rup=1,  std=3.20438e-05
    cd_100 =   1/(1.0129240686314567 - 0.0023339112881583077*gamma)
    # Rup=1.5,  std=1.75254e-05
    cd_150 =   1/(1.005933078723958 - 7.929354028900166e-05*gamma)
    # Rup=2,  std=2.21349e-06
    cd_200 =   1/(1.004296035576616 - 0.0006527109040944512/gamma)
    # Rup=2.5,  std=1.49821e-06
    cd_250 =   1/(1.0025011467929128 + 0.0005677730519755054*log(gamma))
    # Rup=3,  std=4.16526e-07
    cd_300 =   0.998188849337407 - 0.0005288719430737602*log(gamma)
    
    cdL = [ cd_075, cd_100, cd_150, cd_200, cd_250, cd_300]
    return interp1d( RupL , cdL, kind=2, fill_value="extrapolate")( Rup )



if __name__ == "__main__": #Self Test
    import pylab
    import numpy as np
    #from Cd_NASA_33_548 import cd_nasa_1973
    
    gammaL = [1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.5, 1.67]

    cdD = {} # index=Rup, value=CD
    cdD[0.75] = [0.9857159, 0.9859911, 0.9862749, 0.9865668, 0.9868662, 0.9871727, 0.9874859, 0.9881307, 0.9892763]
    cdD[1] = [0.9897993, 0.989885, 0.989977, 0.9900752, 0.9901793, 0.990289, 0.990404, 0.9906493, 0.9911086]
    cdD[1.5] = [0.9942151, 0.9942037, 0.9941956, 0.9941907, 0.9941889, 0.99419, 0.9941941, 0.9942106, 0.9942627]
    cdD[2] = [0.9963129, 0.9962867, 0.9962624, 0.9962398, 0.996219, 0.9961998, 0.9961823, 0.9961521, 0.9961147]
    cdD[2.5] = [0.997453, 0.9974271, 0.9974023, 0.9973785, 0.9973558, 0.9973341, 0.9973134, 0.997275, 0.9972184]
    cdD[3] = [0.9981376, 0.9981148, 0.9980927, 0.9980713, 0.9980505, 0.9980305, 0.998011, 0.9979742, 0.9979172]

    RupL = sorted( list( cdD.keys() ) )
    
    
    pylab.figure( figsize=(7,6) )
    
    MARKERL = ['o','v','^','<','>','d','X','P','s','p','*','.']
    COLORL = ['g','c','b','y','#FFA500','m','r']
    
    gL = [1.1 + i*0.01 for i in range(58)]
    for i,Rup in enumerate(reversed(RupL)):
        color = COLORL[ i % len(COLORL) ]
        pylab.plot( gammaL, cdD[Rup], 's', label='Rup=%g'%Rup, color=color )
        
        calcL = [get_Cd( Rup=Rup, gamma=g ) for g in gL]
        pylab.plot( gL, calcL, '-', color=color )

        #pylab.plot( gammaL, [cd_nasa_1973( Rup )]*len(gammaL), 'D', color=color, markersize=8 )
        
    
    pylab.title('Cd of Nozzle Throat')
    pylab.xlabel('gamma')
    pylab.ylabel('Cd')
    pylab.legend(loc='lower right')
    pylab.grid(True)
    pylab.ylim( bottom=0.984 )
    
    # ----------------------------------------------------------------------------
    RupArr = np.linspace(0.75, 3, 50)
    fig = pylab.figure( figsize=(4,4) )
    
    for gamma in [1.4, 1.3, 1.2]:
        cdL = [ get_Cd( Rup=Rup, gamma=gamma ) for Rup in RupArr ]
        pylab.plot( RupArr, cdL, '-', label='gamma=%g'%gamma )
    
    pylab.title('Cd of Nozzle Throat (Simple Model)')
    pylab.xlabel('Upstream Radius Ratio (RupThroat)')
    pylab.ylabel('Cd')
    pylab.legend(loc='lower right')
    pylab.grid(True)
    fig.tight_layout()
    pylab.savefig( 'cd_throat.png', dpi=300 )
    
    # ----------------------------------------------------------------------------
    pylab.show()
    
    
            
