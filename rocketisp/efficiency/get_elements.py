
from rocketcea.input_cards import oxCards, fuelCards, propCards

good_set = set( ['F', 'C', 'O', 'N', 'CL', 'H', 'P', 'AL','B'] )

def get_elements( prop_name ):
    """
    Return a list of elements in given propellant name.
    For example MMH returns ['H', 'N', 'C'].
    """
    element_set = set()
    if prop_name.upper() in ['A50','UDMH']:
        return ['C','H','N']
    elif prop_name.upper() in ['AP']:
        return ['H','N','CL','O']
    elif prop_name.upper() in ['AIR']:
        return ['N','O']
    elif prop_name.upper().startswith('MON'):
        return ['N','O']
    
    
    for cardD in [oxCards, fuelCards, propCards]:
        if prop_name in cardD:
            cardL = cardD[ prop_name ]
            for card in cardL:
                for s in card.split():
                    if s in good_set:
                        element_set.add( s )
        
    return list( element_set )

def get_ox_fuel_groupname( oxName, fuelName ):
    """
    Given an (oxName, fuelName) pair, return group name.
    For example N2O4/MMH returns CHNO.
    """
    return ''.join( sorted( list( set( get_elements( oxName ) + get_elements( fuelName ) ) ) ) )

fuelL = ['A50','CH4','C2H6','Ethanol','Methanol','MMH','MHF3','N2H4','NH3','LH2','Propane','UDMH','RP1']
oxL = ['N2O4','LOX','MON10','MON25','MON30','N2O','IRFNA','CLF5','F2']

def get_ox_fuel_pair_in_group( group_name ):
    """
    Return an ox/fuel pair (oxName, fuelName) that is in group_name.
    If no ox/fuel pair present, then return (None, None).
    """
    if group_name == "All":
        return 'N2O4','MMH'
    
    for fuelName in fuelL:
        for oxName in oxL:
            gname = get_ox_fuel_groupname( oxName, fuelName )
            
            if group_name == gname:
                return oxName, fuelName
    return None, None

if __name__ == "__main__":

    #for name in sorted( list(oxCards.keys())):
    #    print(name, get_elements(name))
    
    group_set = set()
    for oxName in oxL:
        for fuelName in fuelL:
            groupName = get_ox_fuel_groupname( oxName, fuelName )
            group_set.add( groupName )
            
            oL = get_elements( oxName )
            fL = get_elements( fuelName )
            print('%20s'%(oxName + '/' + fuelName), '%4s'%groupName, '  ox list=',oL,'  fuel list=',fL )
    
    print('group_set =', group_set)
    
    print('get_ox_fuel_pair_in_group( "HO" ) =',get_ox_fuel_pair_in_group( "HO" ))
            
            
            