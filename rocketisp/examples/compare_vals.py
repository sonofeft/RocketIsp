
def compare_header():
    print( '%20s  %12s  %12s  %12s  %12s'%("Descriiption", "Data", "RocketIsp",  "Calc/Data", "% Error") )
    print( '%20s  %12s  %12s  %12s  %12s'%("============", "====", "=========",  "=========", "=======") )
    
def compare( desc, data, calc ):
    d = '%g'%data
    c = '%g'%calc
    try:
        ratio = '%g'%(calc/data, )
    except:
        ratio = '???'
        
    try:
        ierr = int(100000 * (calc - data)/data)
        pcerr = '%g'%(ierr/1000.0,) + ' %'
    except:
        pcerr = '??? %'
        
    print( '%20s  %12s  %12s  %12s  %12s'%(desc, d, c, ratio, pcerr) )
