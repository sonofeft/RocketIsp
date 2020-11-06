

def is_float( val ):
    """If val can be considered a float, return True, otherwise False"""
    try:
        v = float(val)
        return True
    except:
        return False
