"""
ReadTheDocs needs to build sphinx docs, but has trouble installing RocketCEA.
This mocks the nozzle separation functions.
"""


def ambientCf(gam=1.25, epsTot=20.0, Pc=200.0, Pamb=14.7):
    
    Cf, CfOverCfvac, mode = 1.5, 0.95, 'Gibberish'
    return Cf, CfOverCfvac, mode


def sepNozzleCf(gam=1.25, epsTot=20.0, Pc=200.0, Pamb=14.7):
    
    CfOvCfvacAtEsep, CfOvCfvac, Cfsep, CfiVac, CfiAmbSimple,CfVac, epsSep, Psep = \
        0.755981, 0.700438, 1.24907, 1.65225, 1.3002, 1.78327, 5.98724, 5.56034 
    return CfOvCfvacAtEsep, CfOvCfvac, Cf, CfiVac, CfiAmbSimple, CfVac, epsSep, Psep


