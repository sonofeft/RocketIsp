
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
        dev_tests()


See:
      https://docs.python.org/2/library/unittest.html
         or
      https://docs.python.org/dev/library/unittest.html
for more assert options
"""

import sys, os


from rocketisp.efficiency.eff_vaporization import fracVaporized, calc_C1_C2

import rocketisp.efficiency.effBL_NASA_SP8120
import rocketisp.efficiency.calc_noz_kinetics
import rocketisp.efficiency.eff_divergence
import rocketisp.efficiency.eff_pulsing
import rocketisp.efficiency.get_elements
import rocketisp.nozzle.huzel_data
import rocketisp.nozzle.six_opt_parab


class MyTest(unittest.TestCase):

    def test_main_effBL_NASA_SP8120(self):
        
        try:
            if 'TRAVIS' not in os.environ:
                rocketisp.efficiency.effBL_NASA_SP8120.dev_tests( do_show=False )            
        except:
            raise Exception('ERROR... failed in __main__ routine')

    def test_main_calc_noz_kinetics(self):
        
        try:
            if 'TRAVIS' not in os.environ:
                rocketisp.efficiency.calc_noz_kinetics.dev_tests()
        except:
            raise Exception('ERROR... failed in __main__ routine')

    def test_main_eff_divergence(self):
        
        try:
            if 'TRAVIS' not in os.environ:
                rocketisp.efficiency.eff_divergence.dev_tests( do_show=False )
        except:
            raise Exception('ERROR... failed in __main__ routine')

    def test_main_eff_pulsing(self):
        
        try:
            if 'TRAVIS' not in os.environ:
                rocketisp.efficiency.eff_pulsing.dev_tests( do_show=False )
        except:
            raise Exception('ERROR... failed in __main__ routine')

    
    def test_main_eff_vaporization(self):
        
        y_test = fracVaporized( 10.0 )
        self.assertAlmostEqual(y_test, 0.849915, places=4)


    def test_main_get_elements(self):
        
        try:
            if 'TRAVIS' not in os.environ:
                rocketisp.efficiency.get_elements.dev_tests()
        except:
            raise Exception('ERROR... failed in __main__ routine')
        
    def test_main_huzel_data(self):
        
        try:
            if 'TRAVIS' not in os.environ:
                rocketisp.nozzle.huzel_data.dev_tests()
        except:
            raise Exception('ERROR... failed in __main__ routine')
        
    def test_main_six_opt_parab(self):
        
        try:
            if 'TRAVIS' not in os.environ:
                rocketisp.nozzle.six_opt_parab.dev_tests( do_show=False )
        except:
            raise Exception('ERROR... failed in __main__ routine')
        

if __name__ == '__main__':
    # Can test just this file from command prompt
    #  or it can be part of test discovery from nose, unittest, pytest, etc.
    unittest.main()

