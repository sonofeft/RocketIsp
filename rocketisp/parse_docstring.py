from rocketisp.unit_conv_data import get_category

def get_desc_and_units( doc_str ):
    """
    Given a class __doc__ string, parse the definitions and units of each input parameter.
    return descD and unitsD dictionaries.
    (only recognize units in unit_conv_data)
    """
    descD = {}       # key=variable name, value=description from doc string of class_module
    unitsD = {}      # key=variable name, value=internal units from doc string of class_module
    is_inputD = {}   # key=variable name, value=flag indicating an input
    
    dL = doc_str.splitlines()

    for s in dL:
        s = s.strip()
        if s.startswith(':param ') or s.startswith(':ivar '):
            if s.startswith(':param '):
                is_input = True
                s = s.replace(':param ','')
            else:
                is_input = False
                s = s.replace(':ivar ','')
            sL = s.split(':')
            if len(sL) > 1:
                name = sL[0]
                ssL = sL[1].split(',')
                
                # only recognize units in unit_conv_data
                if len(ssL)>1 and get_category(ssL[0].strip()):
                    units = ssL[0].strip()
                    desc = ','.join( ssL[1:] ).strip()
                else:
                    units = ''
                    desc = sL[1].strip()
                unitsD[name] = units 
                descD[name] = desc
                is_inputD[name] = is_input
            
    return descD, unitsD, is_inputD
    
if __name__ == "__main__":
    from rocketisp.geometry import Geometry
    from rocketisp.injector import Injector
    
    descD, unitsD, is_inputD = get_desc_and_units( Geometry.__doc__ )
    for name, desc in descD.items():
        print( name, ' inp=',is_inputD[name], unitsD[name], desc )
    