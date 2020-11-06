
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
        old_sys_argv = list(sys.argv)
        sys.argv = list(sys.argv)
        sys.argv.append('suppress_show')
        
        try:
            #runpy = imp.load_source('__main__', os.path.join(up_one, 'efficiency', 'effBL_NASA_SP8120.py') )
            if 'TRAVIS' not in os.environ:
                runpy = imp.load_source('__main__',  rocketisp.efficiency.effBL_NASA_SP8120.__file__)

            
        except:
            raise Exception('ERROR... failed in __main__ routine')
        finally:
            sys.argv = old_sys_argv

    def test_main_calc_noz_kinetics(self):
        old_sys_argv = list(sys.argv)
        sys.argv = list(sys.argv)
        sys.argv.append('suppress_show')
        
        try:
            #runpy = imp.load_source('__main__', os.path.join(up_one, 'efficiency', 'calc_noz_kinetics.py') )
            if 'TRAVIS' not in os.environ:
                runpy = imp.load_source('__main__',  rocketisp.efficiency.calc_noz_kinetics.__file__)
        except:
            raise Exception('ERROR... failed in __main__ routine')
        finally:
            sys.argv = old_sys_argv

    def test_main_eff_divergence(self):
        old_sys_argv = list(sys.argv)
        sys.argv = list(sys.argv)
        sys.argv.append('suppress_show')
        
        try:
            #runpy = imp.load_source('__main__', os.path.join(up_one, 'efficiency', 'eff_divergence.py') )
            if 'TRAVIS' not in os.environ:
                runpy = imp.load_source('__main__',  rocketisp.efficiency.eff_divergence.__file__)
        except:
            raise Exception('ERROR... failed in __main__ routine')
        finally:
            sys.argv = old_sys_argv

    def test_main_eff_pulsing(self):
        old_sys_argv = list(sys.argv)
        sys.argv = list(sys.argv)
        sys.argv.append('suppress_show')
        
        try:
            #runpy = imp.load_source('__main__', os.path.join(up_one, 'efficiency', 'eff_pulsing.py') )
            if 'TRAVIS' not in os.environ:
                runpy = imp.load_source('__main__',  rocketisp.efficiency.eff_pulsing.__file__)
        except:
            raise Exception('ERROR... failed in __main__ routine')
        finally:
            sys.argv = old_sys_argv

    
    def test_main_eff_vaporization(self):
        
        y_test = fracVaporized( 10.0 )
        self.assertAlmostEqual(y_test, 0.849915, places=4)


    def test_main_get_elements(self):
        old_sys_argv = list(sys.argv)
        sys.argv = list(sys.argv)
        sys.argv.append('suppress_show')
        
        try:
            #runpy = imp.load_source('__main__', os.path.join(up_one, 'efficiency', 'get_elements.py') )
            if 'TRAVIS' not in os.environ:
                runpy = imp.load_source('__main__',  rocketisp.efficiency.get_elements.__file__)
        except:
            raise Exception('ERROR... failed in __main__ routine')
        finally:
            sys.argv = old_sys_argv
        
    def test_main_huzel_data(self):
        old_sys_argv = list(sys.argv)
        sys.argv = list(sys.argv)
        sys.argv.append('suppress_show')
        
        try:
            #runpy = imp.load_source('__main__', os.path.join(up_one, 'nozzle', 'huzel_data.py') )
            if 'TRAVIS' not in os.environ:
                runpy = imp.load_source('__main__',  rocketisp.nozzle.huzel_data.__file__)
        except:
            raise Exception('ERROR... failed in __main__ routine')
        finally:
            sys.argv = old_sys_argv
        
    def test_main_six_opt_parab(self):
        old_sys_argv = list(sys.argv)
        sys.argv = list(sys.argv)
        sys.argv.append('suppress_show')
        
        try:
            #runpy = imp.load_source('__main__', os.path.join(up_one, 'nozzle', 'six_opt_parab.py') )
            if 'TRAVIS' not in os.environ:
                runpy = imp.load_source('__main__',  rocketisp.nozzle.six_opt_parab.__file__)
        except:
            raise Exception('ERROR... failed in __main__ routine')
        finally:
            sys.argv = old_sys_argv
        

if __name__ == '__main__':
    # Can test just this file from command prompt
    #  or it can be part of test discovery from nose, unittest, pytest, etc.
    unittest.main()

