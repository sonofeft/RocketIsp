
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

from rocketisp.geometry import Geometry
import rocketisp.geometry

class MyTest(unittest.TestCase):


    def test_should_always_pass_cleanly(self):
        """Should always pass cleanly."""
        pass

    def test_limit_chamber_length(self):
        """test limit chamber length"""
        
        # SSME Geometry
        G = Geometry(Rthrt=5.1527, CR=3.0, eps=77.5,  LnozInp=121,
             RupThroat=1.0, RdwnThroat=0.392, RchmConv=1.73921, cham_conv_deg=25.42,
             LchmOvrDt=2.4842/2, LchmMin=100.0)
        
        G.summ_print()
        self.assertAlmostEqual(G.Lcham, 100, places=1)

    def test_SSME_Geometry(self):
        """test SSME Geometry"""
        # SSME Geometry
        G = Geometry(Rthrt=5.1527, CR=3.0, eps=77.5,  LnozInp=121,
             RupThroat=1.0, RdwnThroat=0.392, RchmConv=1.73921, cham_conv_deg=25.42,
             LchmOvrDt=2.4842/2)
        self.assertAlmostEqual(G.Vcham, 2192.66, places=1)
        self.assertAlmostEqual(G.pcentBell, 80.6341, places=3)
        
        G.plot_geometry(title='Geometry', png_name='', do_show=False, show_grid=True)
        
        G.reset_attr('Rthrt', 2.0)
        self.assertAlmostEqual(G('Rthrt'), 2, places=1)
        
    def test_check_nozzle_contour(self):
        """test check nozzle contour"""
        # Apollo SPS
        geomObj = Geometry(Rthrt=1,
                   CR=2.5, eps=62.5,  pcentBell=75, 
                   RupThroat=1.5, RdwnThroat=1.0, RchmConv=1.0, cham_conv_deg=30,
                   LchmOvrDt=3.10, LchmMin=2.0, LchamberInp=None)
        
        noz = geomObj.getNozObj()
        noz.plot_geom( do_show=False, save_to_png=False )
        
        self.assertAlmostEqual(noz.angCone, 19.709, places=2)
    
    def test__main__(self):
        old_sys_argv = list(sys.argv)
        sys.argv = list(sys.argv)
        sys.argv.append('suppress_show')
        
        try:
            #runpy = imp.load_source('__main__', os.path.join(up_one, 'geometry.py') )
            if 'TRAVIS' not in os.environ:
                runpy = imp.load_source('__main__', rocketisp.geometry.__file__ )
            
        except:
            raise Exception('ERROR... failed in __main__ routine')
        finally:
            sys.argv = old_sys_argv


        

if __name__ == '__main__':
    # Can test just this file from command prompt
    #  or it can be part of test discovery from nose, unittest, pytest, etc.
    unittest.main()

