#!/usr/bin/env python
# -*- coding: ascii -*-

r"""
RocketIsp calculates delivered Isp for liquid rocket thrust chambers.

RocketIsp is a simplified JANNAF approach to calculating delivered
specific impulse (Isp) for a liquid rocket thrust chamber.

RocketIsp
Copyright (C) 2020  Applied Python

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
here = os.path.abspath(os.path.dirname(__file__))

__author__ = 'Charlie Taylor'
__copyright__ = 'Copyright (c) 2020 Charlie Taylor'
__license__ = 'GPL-3'
exec( open(os.path.join( here,'_version.py' )).read() )  # creates local __version__ variable
__email__ = "cet@appliedpython.com"
__status__ = "4 - Beta" # "3 - Alpha", "4 - Beta", "5 - Production/Stable"

from math import pi
from scipy import optimize

from rocketcea.cea_obj import CEA_Obj
from rocketisp.efficiency.eff_pulsing import eff_pulse
from rocketisp.efficiency.eff_divergence import eff_div
from rocketisp.efficiency.effBL_NASA_SP8120 import eff_bl_NASA, regen_corrected_bl
from rocketisp.efficiency.calc_All_fracKin import calc_fracKin
from rocketisp.nozzle.cd_throat import get_Cd

class RocketThruster(object):
    """RocketIsp calculates delivered Isp for liquid rocket thrust chambers."""

    def __init__(self, oxName='N2O4', fuelName='MMH', eff_ERE=0.97,
                 Pc=500, eps=20, pcentBell=80, MR=1.5,
                 Rthrt=1, RupOverRt=1.5,
                 noz_regen_eps=1.0,
                 pulse_sec=float('inf'), pulse_quality=0.8):
        """
        Calculate delivered thrust chamber Isp by simplified JANNAF method.

        :param oxName: oxidizer name
        :param fuelName: fuel name
        :param eff_ERE: energy release efficiency (calc'd elsewhere)
        :param Pc: chamber pressure (psia)
        :param eps: nozzle area ratio
        :param pcentBell: nozzle percent bell
        :param MR: mixture ratio (ox flowrate / fuel flowrate)
        :param Rthrt: throat radius (in)
        :param RupOverRt: upstream radius / throat radius
        :param noz_regen_eps: regen cooled nozzle area ratio
        :param pulse_sec: duration of pulsing engine (default = infinity)
        :param pulse_quality: on a scale of 0.0 to 1.0, how good is engine at pulsing
        :type oxName: str
        :type fuelName: str
        :type eff_ERE: float
        :type Pc: float
        :type eps: float
        :type pcentBell: float
        :type MR: float
        :type Rthrt: float
        :type RupOverRt: float
        :type noz_regen_eps: float
        :type pulse_sec: float
        :type pulse_quality: float
        :return: RocketThruster object
        :rtype: RocketThruster
        """
        self.oxName        = oxName
        self.fuelName      = fuelName
        self.iprop         = oxName + '/' + fuelName
        self.eff_ERE       = eff_ERE
        self.Pc            = Pc
        self.eps           = eps
        self.pcentBell     = pcentBell
        self.MR            = MR
        self.Rthrt         = Rthrt
        self.RupOverRt     = RupOverRt
        self.pulse_sec     = pulse_sec
        self.pulse_quality = pulse_quality  
        
        self.noz_regen_eps = noz_regen_eps
        
        self.ceaObj = CEA_Obj(oxName=oxName, fuelName=fuelName)
        
        self.calc_all_eff()
    
    def set_Fvac(self, FvacLbf=500.0, quick_set=True):
        """Adjust Rthrt in order to get FvacLbf exactly"""
        
        def f_diff( Rt ):
            self.Rthrt = Rt
            self.calc_all_eff()
            return FvacLbf - self.FvacLbf
        
        At_guess = self.At * FvacLbf / self.FvacLbf
        Rt_guess = (At_guess/pi)**0.5
        
        if quick_set:
            # often converges in just a few iterations.
            f_diff( Rt_guess )
            for _ in range( 2 ):
                At_guess = self.At * FvacLbf / self.FvacLbf
                Rt_guess = (At_guess/pi)**0.5
                f_diff( Rt_guess )
            
        else:
            # demand convergence to a tolerance with a root solver.
            Rt_min = Rt_guess/1.4
            Rt_max = Rt_guess*1.4
            
            sol = optimize.root_scalar(f_diff, x0=Rt_guess, bracket=[Rt_min, Rt_max], 
                                       xtol=FvacLbf/1.0E8, method='brentq')
            #print('sol.root=%g, sol.iterations=%g, sol.function_calls=%g'%(sol.root, sol.iterations, sol.function_calls))
            f_diff( sol.root )
    
    def calc_all_eff(self):
        
        self.At = pi * self.Rthrt**2
        
        self.eff_div = eff_div( eps=self.eps, pcBell=self.pcentBell)
        
        if self.pulse_sec < 1.0E10:
            self.eff_pulse = eff_pulse( pulse_sec=self.pulse_sec, pulse_quality=self.pulse_quality)
        else:
            self.eff_pulse = 1.0
            
        self.eff_BL = eff_bl_NASA( Dt=self.Rthrt*2.0, Pc=self.Pc, eps=self.eps)
        if self.noz_regen_eps > 1.0:
            self.eff_BL = regen_corrected_bl( eff_bl=self.eff_BL, eps=self.eps, noz_regen_eps=self.noz_regen_eps )
        
        self.fracKin = calc_fracKin(self.ceaObj, Pc=self.Pc, eps=self.eps, 
                                    Rthrt=self.Rthrt, pcentBell=self.pcentBell, 
                                    MR=self.MR)
                                    
        self.IspODE,self.cstarODE,self.TcODE,self.MWchm,self.gammaChm = \
                self.ceaObj.get_IvacCstrTc_ChmMwGam( Pc=self.Pc, MR=self.MR, eps=self.eps)
        self.IspODF,_,_ = self.ceaObj.getFrozen_IvacCstrTc( Pc=self.Pc, MR=self.MR, eps=self.eps, frozenAtThroat=0)
        
        self.IspODK = self.IspODF + self.fracKin * (self.IspODE-self.IspODF)

        self.eff_kin = self.IspODK / self.IspODE
        
        self.eff_nozzle = self.eff_div * self.eff_BL * self.eff_kin
        self.eff_Isp    = self.eff_ERE * self.eff_nozzle * self.eff_pulse
        
        self.IspDel = self.IspODE * self.eff_Isp
        
        self.Cd_thrt = get_Cd( RWTU=self.RupOverRt, gamma=self.gammaChm )
        self.cstarDel = self.cstarODE * self.eff_ERE / self.Cd_thrt
        
        self.wdotTot = self.Pc * self.At * 32.174 / self.cstarDel
        self.FvacLbf = self.wdotTot * self.IspDel

        self.wdotOx  = self.wdotTot * self.MR / (1.0 + self.MR)
        self.wdotFl = self.wdotTot - self.wdotOx 
        
    def summ_print(self):
        self.xxx = ''
        print('-'*60)
        print('     %s Delivered Isp'%self.iprop)
        print('     ------   Input  -------')
        #print( 'oxName        =', self.oxName)
        #print( 'fuelName      =', self.fuelName)
        print( 'eff_ERE       =', self.eff_ERE,"energy release efficiency (calc'd elsewhere)")
        print( 'Pc            =', self.Pc, 'psia')
        print( 'eps           =', self.eps)
        print( 'pcentBell     =', self.pcentBell)
        print( 'MR            =', self.MR)
        print( 'Rthrt         =', self.Rthrt, 'in  throat radius')
        print( 'At            =', self.At, 'in**2  throat area')
        print( 'RupOverRt     =', self.RupOverRt, ' Rupstream / Rthrt')
            
        if self.pulse_sec < 1.0E10:
            print( 'pulse_sec     =', self.pulse_sec, 'sec')
            print( 'pulse_quality =', self.pulse_quality )
            
        print( 'noz_regen_eps =', self.noz_regen_eps,'regen-cooled nozzle area ratio')
        print( 'xxx           =', self.xxx)
            
            
        # ------------------ Output ------------------
        print('     ------   Output  -------')
        
        print( 'IspDel        =', '%.2f'%self.IspDel, 'sec  delivered Isp')
        print()
        print( 'IspODE        =', '%.2f'%self.IspODE, 'sec  one dimensional equilibrium Isp')
        print( 'IspODK        =', '%.2f'%self.IspODK, 'sec  kinetic Isp (fracKin=%g)'%self.fracKin)
        print( 'IspODF        =', '%.2f'%self.IspODF, 'sec  frozen Isp')
        print()
        print( 'Cd throat     =', '%.5f'%self.Cd_thrt, ' throat Cd')
        print( 'gamma chm     =', '%.5f'%self.gammaChm, ' chamber gamma (Cp/Cv)')
        print( 'C* Del        =', '%.1f'%self.cstarDel,'ft/sec  delivered characteristic velocity')
        print( 'C* ODE        =', '%.1f'%self.cstarODE,'ft/sec  ideal characteristic velocity')
        
        print( 'FvacLbf       =', '%g'%self.FvacLbf, 'lbf  vacuum thrust')
        print( 'wdot          =', '%g'%self.wdotTot, 'lbm/sec total propellant flow rate')
        print( 'wdotOx        =', '%g'%self.wdotOx, 'lbm/sec total oxidizer flow rate')
        print( 'wdotFl        =', '%g'%self.wdotFl, 'lbm/sec total fuel flow rate')
        print()
        print( 'eff_Isp       =', '%.5f'%self.eff_Isp,'overall Isp efficiency')
        print( 'eff_nozzle    =', '%.5f'%self.eff_nozzle,'nozzle efficiency')
        print('-------------- nozzle efficiency breakdown ------------')
        print( 'eff_div       =', '%.5f'%self.eff_div, 'nozzle divergence efficiency')
        print( 'eff_BL        =', '%.5f'%self.eff_BL,  'nozzle boundary layer efficiency')
        print( 'eff_kin       =', '%.5f'%self.eff_kin, 'nozzle kinetic efficiency')
        if self.pulse_sec < 1.0E10:
            print( 'eff_pulse     =', '%.5f'%self.eff_pulse)
        print( 'xxx           =', self.xxx)
        print( 'xxx           =', self.xxx)
        
        

if __name__ == '__main__':
    C = RocketThruster(oxName='N2O4', fuelName='MMH', Pc=500, 
                 eps=20, pcentBell=80, MR=1.5,
                 noz_regen_eps=1.0,
                 Rthrt=1, RupOverRt=1.5,
                 pulse_sec=float('inf'), pulse_quality=0.8)
    C.set_Fvac( 10000.0, quick_set=True )
    C.summ_print()
