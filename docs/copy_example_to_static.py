import sys, os
here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find rocketisp development version

src_dir = os.path.join( up_one, 'rocketisp', 'examples' )
target_dir = os.path.join( here, '_static', 'example_scripts' )

if len(sys.argv) < 2:
    print('ERROR... no filename given to copy')
    sys.exit()
    
fname = sys.argv[1]
print( 'Copying', fname, 'to ',target_dir )
target_name = os.path.join( target_dir, fname )

contentL = open( os.path.join(src_dir, fname), 'r' ).readlines()

fOut = open(target_name, 'w')
for line in contentL:
    if line.startswith('# ...END...'):
        break
    fOut.write( line.rstrip() + '\n' )
fOut.close()
