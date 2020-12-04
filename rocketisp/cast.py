import math

def max_precision_float_str( value, num_decimals=3, soft_len_limit=5 ):
    """Try to return a string with num_decimals and of length <= soft_len_limit."""
    s = str( round( value, num_decimals ) )
    
    while len(s) > soft_len_limit:
        num_decimals -= 1
        if num_decimals < 0:
            break
        s = str( round( value, num_decimals ) )
    
    return s

def rounded_number(value, significant_digits=3):
    return round(value, significant_digits - int(math.floor(math.log10(abs(value)))) - 1)
    
def boolCast( val=True ):
    
    sval = '%s'%val
    sval = sval.lower()
    if sval in ['false','0','null','None']:
        return False
    
    if val:
        return True
    else:
        return False

def is_bool( val ):
    
    if type(val) == type(True):
        return True
    else:
        return False

def intCast( val=0 ):
    try:
        return int(val)
    except:
        return 0
        
def floatCast( val=0.0 ):
    try:
        return float(val)
    except:
        return float('-inf')

def is_int( ival ):
    
    if type(ival)==type(11):
        return 1
    
    if is_bool( ival ):
        return 0
    
    if type(ival)==type('string'):
        if ival.find('.')>=0:
            return 0
        try:
            i = int( ival )
            return 1
        except:
            pass
    
    try:
        if intCast( ival) == int(ival):
            return 1
    except:
        pass
        
    return 0


def is_float( fval ):
    
    if type(fval)==type(11.11):
        return 1
    
    if is_bool( fval ):
        #print('        Rejecting float as a boolean', fval, type(fval) )
        return 0
    
    try:
        x = float( fval ) # accept int as float
        #print('x=',x,'   float( fval )=',float( fval ))
        if not math.isnan( float( fval) ): # do NOT accept nan as a float
            return 1
    except:
        pass
        
    return 0

if __name__ == "__main__":
    '''https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
    Command to parse                        Is it a float?  Comment
    --------------------------------------  --------------- ------------
    print(isfloat("1234567"))               True 
    print(isfloat("123.456"))               True
    print(isfloat("123.E4"))                True
    print(isfloat(".1"))                    True
    print(isfloat("6.523537535629999e-07")) True
    print(isfloat("6e777777"))              True            This is same as Inf
    print(isfloat("-iNF"))                  True
    print(isfloat("1.797693e+308"))         True
    print(isfloat("infinity"))              True
    print(isfloat("0E0"))                   True
    print(isfloat("+1e1"))                  True

    print(isfloat(True))                    NOT True            Boolean is a float
    print(isfloat("NaN"))                   NOT True            nan is also float
    print(isfloat("+1e1^5"))                False
    print(isfloat("+1e1.3"))                False
    print(isfloat("+1.3P1"))                False
    print(isfloat("-+1"))                   False
    print(isfloat("(1)"))                   False           brackets not interpreted
    print(isfloat(""))                      False
    print(isfloat("NaNananana BATMAN"))     False
    print(isfloat("1,234"))                 False
    print(isfloat("NULL"))                  False           case insensitive
    print(isfloat(",1"))                    False           
    print(isfloat("123.EE4"))               False           
    print(isfloat("infinity and BEYOND"))   False
    print(isfloat("12.34.56"))              False           Two dots not allowed.
    print(isfloat("#56"))                   False
    print(isfloat("56%"))                   False
    print(isfloat("x86E0"))                 False
    print(isfloat("86-5"))                  False
    print(isfloat("True"))                  False           Boolean is not a float.   
    '''

    good_float_L = ["1234567","123.456","123.E4",".1","6.523537535629999e-07","6e777777","-iNF",
                    "1.797693e+308","infinity","0E0","+1e1", 123] # accept int as float
    for s in good_float_L:
        if not is_float(s):
            print('Failed good is_float for string = "%s"'%s)

    
    bad_float_L = [True, False,"NaN","+1e1^5","+1e1.3","+1.3P1","-+1","(1)","","NaNananana BATMAN","1,234",
                      "NULL",",1","123.EE4","infinity and BEYOND","12.34.56","#56","56%","x86E0","86-5","True"]
    for s in bad_float_L:
        if  is_float(s):
            print('Failed BAD is_float for string = "%s"'%s, 'float(val)=',float(s),'  type(val)=',type(s))


    print('----------max_precision_float_str( value, num_decimals=3 )-------------')
    
    for value in [1.0, 1.2, 1.23, 1.234, 1.2344, 1.2345, 1.234500001, 
                  1.23456, 12.3456, 123.456, 1234.56, 12345.6, 54321.23456]:
        print( value, max_precision_float_str( value, num_decimals=3, soft_len_limit=5 ),
               rounded_number(value, significant_digits=4))
    