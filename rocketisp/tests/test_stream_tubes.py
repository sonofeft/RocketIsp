
import unittest
# import unittest2 as unittest # for versions of python < 2.7

"""
        Method                            Checks that
self.assertEqual(a, b)                      a == b   
self.assertNotEqual(a, b)                   a != b   
self.assertTrue(x)                          bool(x) is True  
self.assertFalse(x)                         bool(x) is False     
self.assertIs(a, b)                         a is b
self.assertIsNot(a, b)                      a is not b
self.assertIsNone(x)                        x is None 
self.assertIsNotNone(x)                     x is not None 
self.assertIn(a, b)                         a in b
self.assertNotIn(a, b)                      a not in b
self.assertIsInstance(a, b)                 isinstance(a, b)  
self.assertNotIsInstance(a, b)              not isinstance(a, b)  
self.assertAlmostEqual(a, b, places=5)      a within 5 decimal places of b
self.assertNotAlmostEqual(a, b, delta=0.1)  a is not within 0.1 of b
self.assertGreater(a, b)                    a is > b
self.assertGreaterEqual(a, b)               a is >= b
self.assertLess(a, b)                       a is < b
self.assertLessEqual(a, b)                  a is <= b

for expected exceptions, use:

with self.assertRaises(Exception):
    blah...blah...blah

with self.assertRaises(KeyError):
    blah...blah...blah

Test if __name__ == "__main__":
    def test__main__(self):
        # loads and runs the bottom section: if __name__ == "__main__"
        runpy = imp.load_source('__main__', os.path.join(up_one, 'filename.py') )


See:
      https://docs.python.org/2/library/unittest.html
         or
      https://docs.python.org/dev/library/unittest.html
for more assert options
"""

import sys, os
import imp

here = os.path.abspath(os.path.dirname(__file__)) # Needed for py.test
up_one = os.path.split( here )[0]  # Needed to find modelps development version
if here not in sys.path[:2]:
    sys.path.insert(0, here)
if up_one not in sys.path[:2]:
    sys.path.insert(0, up_one)

from rocketisp.geometry import Geometry
from rocketisp.efficiencies import Efficiencies
from rocketisp.stream_tubes import CoreStream
import rocketisp.stream_tubes

class MyTest(unittest.TestCase):


    def test_should_always_pass_cleanly(self):
        """Should always pass cleanly."""
        pass


    def test_check_FFC_Isp_values(self):
        """test check FFC Isp values"""
        
        geomObj = Geometry(Rthrt=1,
                           CR=2.5, eps=62.5,  pcentBell=75, 
                           RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                           LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
                           
        effObj = Efficiencies()
        effObj.set_const('ERE', 0.98) # don't know injector details so set effERE=0.98

        # It's an ablative chamber, so some FFC (fuel film cooling) is required... guess about 10%
        C = CoreStream( geomObj=geomObj, effObj=effObj, pcentFFC=10.0, Pamb=0.001,
                        oxName='N2O4', fuelName='A50',  MRcore=1.6, Pc=100 )
        
        C.reset_attr('Pc', 100)
        
        self.assertAlmostEqual(C('IspDel'), 326.5939, places=2)
        self.assertAlmostEqual(C('IspODE'), 338.9201, places=2)
        self.assertAlmostEqual(C('IspODF'), 320.4940, places=2)
    

    def test_check_Isp_values(self):
        """test check Isp values"""
        
        C = CoreStream( geomObj=Geometry(eps=35), 
                effObj=Efficiencies(ERE=0.98, Noz=0.97), 
                oxName='LOX', fuelName='CH4',  MRcore=3.6,
                Pc=500, Pamb=14.7)
        
        self.assertAlmostEqual(C('IspAmb'), 325.1188, places=2)
        self.assertAlmostEqual(C('IspDel'), 345.2795, places=2)
        self.assertAlmostEqual(C('IspODE'), 363.2227, places=2)
        self.assertAlmostEqual(C('IspODF'), 334.1623, places=2)
        
        C.reset_CdThroat( C.CdThroat )
        C.reset_attr('Pamb', C.Pexit+0.06, re_evaluate=True)
        C.reset_attr('Pamb', C.Pexit, re_evaluate=True)
        C.reset_attr('Pamb', 15, re_evaluate=True)
        
    
    def test__main__(self):
        old_sys_argv = list(sys.argv)
        sys.argv = list(sys.argv)
        sys.argv.append('suppress_show')
        
        try:
            #runpy = imp.load_source('__main__', os.path.join(up_one, 'stream_tubes.py') )
            runpy = imp.load_source('__main__',  rocketisp.stream_tubes.__file__)
        except:
            raise Exception('ERROR... failed in __main__ routine')
        finally:
            sys.argv = old_sys_argv


        

if __name__ == '__main__':
    # Can test just this file from command prompt
    #  or it can be part of test discovery from nose, unittest, pytest, etc.
    unittest.main()

