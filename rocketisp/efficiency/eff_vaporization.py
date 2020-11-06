
from math import pi, log

def fracVaporized( genVapLen ):
    #def pcentVaporized( genVapLen ):
    '''
    Curve Fit Results from XYmath 10/06/2020
    calculate fraction vaporized from the generalized chamber length
    Taken from Technical Report R-67, Propellant Vaporization as a Design Criterion
    for Rocket-Engine Combustion Chambers by Richard J. Priem and Marcus F. Heidmann

    y = 100 - (A / (x+B + C/x))**n
        A = 52.80649561778126
        B = 13.663973074318259
        C = -0.008743937330141364
        n = 3.3743031679503477
        x = genVapLen
        y = percent vaporized
        Correlation Coefficient = 0.999522781340404
        Standard Deviation = 1.2720343007164316
        Percent Standard Deviation = 23.79198308501761%
    y = 100 - (52.80649561778126 / (x+13.663973074318259 - 0.008743937330141364/x))**3.3743031679503477

     (x,y)*Wt Weighted Data Set from 10/06/2020.(Only showing weights!=1.0)
     (x,y)*Wt = (0.0429298,1),(0.0996788,3),(0.30053,10),(0.740041,20),
        (1.8828,40),(3.96377,60),(9.00458,80),(15.1686,90),(22.2349,95),
        (31.4792,98),(39.1193,99)*100,(1000,100)
    '''
    x = genVapLen
    
    # turn into fraction vaporized... divide by 100.0
    return (100 - (52.80649561778126 / (x + 13.663973074318259 - 0.008743937330141364/x))**3.3743031679503477) / 100.0

    
def fracVaporized_old_xxx( genVapLen ):
    '''
    calculate fraction vaporized from the generalized chamber length
    Oct 10, 2007: added smoothing between genVapLen ranges
       
    Taken from Technical Report R-67, Propellant Vaporization as a Design Criterion
    for Rocket-Engine Combustion Chambers by Richard J. Priem and Marcus F. Heidmann
    
    '''
    if genVapLen > 10.0:
        return 1.0 - (421.8/(genVapLen+428.5))**45.68
    
    if genVapLen > 1.0:
        return (0.24575* log(genVapLen) + 0.2434) * (0.83029402179819289/0.80926028660328675)
    
    return 0.2434*genVapLen * (0.83029402179819289/0.80926028660328675)

def calc_C1_C2( propObj, TdegR, rho, dHvap, surfTen, visc, MolWt):
    """
    rho==lbm/in**3, dHvap==BTU/lbm, surfTen==lbf/in, visc==lbm/s/ft
    
    CFX = (Pc/300.)**.66 * (Lcham_cyl/CR**.44 + .83*Lcham_conv/(CR**.22 * ShapeFact**.33))

    genVapLen = CFX/(C2*(rDrop/.003)**1.45 * (vel_ips/1200.)**.75)
    """

    C1 = (5.9837E6 * visc * surfTen / rho / 12.0)**0.25

    #C IF ESTIMATED TEMPERATURE RISES ABOVE CRITICAL TEMPERATURE
    #C THEN SET C2 VALUES AT VERY LOW POSITIVE VALUE
    if TdegR >= propObj.Tc:
        C2=1.E-25
    else:
        C2 = ((dHvap/140.0)**0.8)*((MolWt/100.0)**0.35) * (1.0-(TdegR/propObj.Tc))**0.4

    return C1, C2

if __name__ == "__main__": #Self Test
    import sys

    print( '='*44 )
    y_test = fracVaporized( 10.0 )
    print( 'y_test  =',y_test,'for x_test =',10.0 )
    print( 'y_xymath=',0.8499157321136039 )
    print( )
    print( 'y_test should equal y_xymath above.' )
