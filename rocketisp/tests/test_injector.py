
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
from rocketisp.stream_tubes import CoreStream
from rocketisp.efficiencies import Efficiencies
from rocketisp.injector import Injector
import rocketisp.injector

class MyTest(unittest.TestCase):


    def test_should_always_pass_cleanly(self):
        """Should always pass cleanly."""
        pass


    def test_overall_Isp_efficiency(self):
        """test overall Isp efficiency"""
        
        G = Geometry(Rthrt=5.978,
                     CR=2.5, eps=62.5,  pcentBell=75, 
                     RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                     LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
                     
        C = CoreStream( geomObj=G, effObj=Efficiencies(ERE=0.98, Noz=0.96515),  pcentFFC=10.0,
                        oxName='N2O4', fuelName='A50',  MRcore=1.6, Pc=100, Pamb=0.0 )

        I = Injector(C,
                     Tox=None, Tfuel=None, Em=0.8,
                     fdPinjOx=0.25, fdPinjFuel=0.25, dpOxInp=None, dpFuelInp=None,
                     setNelementsBy='acoustics', # can be "acoustics", "elem_density", "input"
                     elemDensInp=5, NelementsInp=100,
                     OxOrfPerEl=1.0, FuelOrfPerEl=1.0, 
                     lolFuelElem=True, 
                     setAcousticFreqBy='mode', # can be "mode" or "freq"
                     desAcousMode='2T', desFreqInp=5000, 
                     CdOxOrf=0.75, CdFuelOrf=0.75, dropCorrOx=0.33, dropCorrFuel=0.33,
                     DorfMin=0.008,
                     LfanOvDorfOx=20.0, LfanOvDorfFuel=20.0)
                     
        self.assertAlmostEqual(I('MolWtOx'), 92.011, places=1)
    
    def test__main__(self):
        old_sys_argv = list(sys.argv)
        sys.argv = list(sys.argv)
        sys.argv.append('suppress_show')
        
        try:
            #runpy = imp.load_source('__main__', os.path.join(up_one, 'injector.py') )
            if 'TRAVIS' not in os.environ:
                runpy = imp.load_source('__main__', rocketisp.injector.__file__)
        except:
            raise Exception('ERROR... failed in __main__ routine')
        finally:
            sys.argv = old_sys_argv


        

if __name__ == '__main__':
    # Can test just this file from command prompt
    #  or it can be part of test discovery from nose, unittest, pytest, etc.
    unittest.main()

