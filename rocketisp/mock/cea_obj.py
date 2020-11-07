


class CEA_Obj(object):
"""
ReadTheDocs needs to build sphinx docs, but has trouble installing RocketCEA.
This mocks the CEA_Obj.
"""
    def __init__(self, propName='', oxName='', fuelName='', fac_CR=None,
        useFastLookup=0, # depricated
        makeOutput=0, make_debug_prints=False):
            
        pass
        
    

    def get_full_cea_output(self, Pc=100.0, MR=1.0, eps=40.0, subar=None, PcOvPe=None,
                            frozen=0, frozenAtThroat=0, short_output=0, show_transport=1,
                            pc_units='psia', output='calories', show_mass_frac=False,
                            fac_CR=None):
        """
        Get the full output file created by CEA. Return as a string.::
        
        #: Pc = combustion end pressure
        #: eps = Nozzle Expansion Area Ratio
        #: pc_units = 'psia', 'bar', 'atm', 'mmh'(mm of mercury)
        #: frozen = flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        #: fac_CR = Contraction Ratio of finite area combustor, (None=infinite)
        """

        # regardless of how run was set up, change makeOutput flag True
        save_flag = self.makeOutput
        self.makeOutput = True
        
        # Allow user to override fac_CR from CEA_Obj __init__
        save_fac_CR = self.fac_CR
        if fac_CR is not None:
            self.fac_CR = fac_CR

        self.setupCards( Pc=Pc, MR=MR, eps=eps, subar=subar, PcOvPe=PcOvPe,
                         frozen=frozen, frozenAtThroat=frozenAtThroat, 
                         short_output=short_output,
                         show_transport=show_transport, pc_units=pc_units,
                         output=output, show_mass_frac=show_mass_frac)

        self.makeOutput = save_flag # restore makeOutput
        self.fac_CR = save_fac_CR   # restore fac_CR

        return open( os.path.join(ROCKETCEA_DATA_DIR,'f.out'),'r').read()


    def get_Pinj_over_Pcomb(self, Pc=100.0, MR=1.0, fac_CR=None):
        """
        Get the pressure ratio of Pinjector / Pchamber.::
        
        #: Pc = combustion end pressure (psia)
        #: fac_CR = Contraction Ratio of finite area combustor, (None=infinite)
        """
        
        # Allow user to override fac_CR from CEA_Obj __init__
        save_fac_CR = self.fac_CR
        if fac_CR is not None:
            self.fac_CR = fac_CR
            
        if self.fac_CR is None:
            print('ERROR in get_Pinj_over_Pcomb... Need value for fac_CR')
            raise Exception('ERROR in get_Pinj_over_Pcomb... Need value for fac_CR')

        self.setupCards( Pc=Pc, MR=MR )

        self.fac_CR = save_fac_CR   # restore fac_CR
        
        Pinj_over_Pcomb = py_cea.prtout.ppp[0] / py_cea.prtout.ppp[1]

        return Pinj_over_Pcomb


    def __call__(self, Pc=100.0, MR=1.0, eps=40.0, frozen=0, frozenAtThroat=0):
        """Returns IspVac(sec) if CEA_Obj is simply called like a function."""
        return 300.0

    def get_IvacCstrTc(self, Pc=100.0, MR=1.0, eps=40.0, frozen=0, frozenAtThroat=0):
        """::

        #: Return the tuple (IspVac, Cstar, Tcomb)in(sec, ft/sec, degR)
        #: Pc = combustion end pressure (psia)
        #: eps = Nozzle Expansion Area Ratio
        #: MR is only used for ox/fuel combos.
        #: frozen = flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        """
        return 300., 5500., 6000.
        return IspVac, Cstar, Tcomb

    def getFrozen_IvacCstrTc(self, Pc=100.0, MR=1.0, eps=40.0, frozenAtThroat=0):
        """::

        #: Return the tuple (IspFrozen, Cstar, Tcomb)in(sec, ft/sec, degR)
        #: Pc = combustion end pressure (psia)
        #: eps = Nozzle Expansion Area Ratio
        #: MR is only used for ox/fuel combos.
        #: frozenAtThroat flag, 0=frozen in chamber, 1=frozen at throat
        """

        return 280., 5500., 6000.
        return IspFrozen, Cstar, Tcomb

    def get_IvacCstrTc_exitMwGam(self, Pc=100.0, MR=1.0, eps=40.0, frozen=0, frozenAtThroat=0):
        """::

        #: return the tuple (IspVac, Cstar, Tcomb, mw, gam)in(sec, ft/sec, degR, lbm/lbmole, -)
        #: Pc = combustion end pressure (psia)
        #: eps = Nozzle Expansion Area Ratio
        #: mw and gam apply to nozzle exit.
        #: MR is only used for ox/fuel combos.
        #: frozen = flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        """

        return 300., 5500., 6000., 30, 1.3
        return IspVac, Cstar, Tcomb, mw, gam


    def get_IvacCstrTc_ChmMwGam(self, Pc=100.0, MR=1.0, eps=40.0):
        """::

        #: return the tuple (IspVac, Cstar, Tcomb, mw, gam)in(sec, ft/sec, degR, lbm/lbmole, -)
        #: Pc = combustion end pressure (psia)
        #: eps = Nozzle Expansion Area Ratio
        #: mw and gam apply to chamber.
        #: MR is only used for ox/fuel combos.
        """
        return 300., 5500., 6000., 30, 1.3
        return IspVac, Cstar, Tcomb, mw, gam

    def get_IvacCstrTc_ThtMwGam(self, Pc=100.0, MR=1.0, eps=40.0):
        """::

        #: return the tuple (IspVac, Cstar, Tcomb, mw, gam)in(sec, ft/sec, degR, lbm/lbmole, -)
        #: Pc = combustion end pressure (psia)
        #: eps = Nozzle Expansion Area Ratio
        #: mw and gam apply to throat.
        #: MR is only used for ox/fuel combos.
        """
        return 300., 5500., 6000., 30, 1.3
        return IspVac, Cstar, Tcomb, mw, gam

    def get_Isp(self, Pc=100.0, MR=1.0, eps=40.0, frozen=0, frozenAtThroat=0):
        """::

        #: return IspVac (sec)
        #: Pc = combustion end pressure (psia)
        #: eps = Nozzle Expansion Area Ratio
        #: MR is only used for ox/fuel combos.
        #: frozen = flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        """
        return 300.
        return IspVac

    def get_Cstar(self, Pc=100.0, MR=1.0):
        """::

        #: return Cstar (ft/sec)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        """
        return 5500.
        return Cstar

    def get_Tcomb(self, Pc=100.0, MR=1.0):
        """::

        #: return Tcomb (degR)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        """
        return 6000.
        return Tcomb

    def get_PcOvPe(self, Pc=100.0, MR=1.0, eps=40.0, frozen=0, frozenAtThroat=0):
        """::

        #: return Pc / Pexit.
        #: Pc = combustion end pressure (psia)
        #: eps = Nozzle Expansion Area Ratio
        #: MR is only used for ox/fuel combos.
        #: frozen = flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        """
        return 300.
        return PcOvPe

    def get_eps_at_PcOvPe(self, Pc=100.0, MR=1.0, PcOvPe=1000.0, frozen=0, frozenAtThroat=0):
        """::

        #: Given a Pc/Pexit, return the Area Ratio that applies.
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: frozen = flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        """
        return 30.
        return eps

    def get_Throat_PcOvPe(self, Pc=100.0, MR=1.0):
        """::

        #: return Pc/Pexit at throat.
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        """
        return 2.0
        return PcOvPe

    def get_MachNumber(self, Pc=100.0, MR=1.0, eps=40.0, frozen=0, frozenAtThroat=0):
        """::

        #: return nozzle exit mach number.
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen = flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        """
        return 3.
        return M

    def get_Chamber_MachNumber(self, Pc=100.0, MR=1.0, fac_CR=None):
        """::

        #: Return  mach numbers at the chamber
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: fac_CR = Contraction Ratio of finite area combustor, (None=infinite)
        """
        return 0.3
        return M

    def get_Temperatures(self, Pc=100.0, MR=1.0,eps=40.0, frozen=0, frozenAtThroat=0):
        """::

        #: Return a list of temperatures at the chamber, throat and exit (degR)
        #: (Note frozen flag determins whether Texit is equilibrium or Frozen temperature)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat flag, 0=frozen in chamber, 1=frozen at throat
        """
        return [5500., 3000., 2000., 2000.]
        return tempList # Tc, Tthroat, Texit


    def get_SonicVelocities(self, Pc=100.0, MR=1.0,eps=40.0, frozen=0, frozenAtThroat=0):
        """::

        #: Return a list of sonic velocities at the chamber, throat and exit (ft/sec)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen = flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        """
        return [5500., 3000., 2000., 2000.]
        return sonicList

    def get_Chamber_SonicVel(self, Pc=100.0, MR=1.0, eps=40.0):
        """::

        #: Return the sonic velocity in the chamber (ft/sec)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        """
        return 5500.
        return sonicList[ 0 ] # 0 == self.i_chm here


    def get_Entropies(self, Pc=100.0, MR=1.0,eps=40.0, frozen=0, frozenAtThroat=0):
        """::

        #: Return a list of entropies at the chamber, throat and exit CAL/(G)(K)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen = flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        """
        return [5500., 3000., 2000., 2000.]
        return sList

    def get_Enthalpies(self, Pc=100.0, MR=1.0,eps=40.0, frozen=0, frozenAtThroat=0):
        """::

        #: Return a list of enthalpies at the chamber, throat and exit (BTU/lbm)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen = flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        """
        return [5500., 3000., 2000., 2000.]
        return hList

    def get_SpeciesMassFractions(self, Pc=100.0, MR=1.0,eps=40.0, 
                                 frozen=0, frozenAtThroat=0, min_fraction=0.000005):
        """::

        #: Returns species mass fractions at the injector face, chamber, throat and exit.
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat flag, 0=frozen in chamber, 1=frozen at throat
        #: Returns 2 dictionaries
        #: molWtD dictionary: index=species: value=molecular weight
        #: massFracD dictionary: index=species: value=[massfrac_injface, massfrac_chm, massfrac_tht, massfrac_exit]
        """
        return {}, {}
        return molWtD, massFracD

    def get_SpeciesMoleFractions(self, Pc=100.0, MR=1.0,eps=40.0, 
                                 frozen=0, frozenAtThroat=0, min_fraction=0.000005):
        """::

        #: Returns species mole fractions at the injector face, chamber, throat and exit.
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat flag, 0=frozen in chamber, 1=frozen at throat
        #: Returns 2 dictionaries
        #: molWtD dictionary: index=species: value=molecular weight
        #: moleFracD dictionary: index=species: value=[molefrac_injface, molefrac_chm, molefrac_tht, molefrac_exit]
        """
        
        return {}, {}
        return molWtD, moleFracD

    def get_Chamber_H(self, Pc=100.0, MR=1.0, eps=40.0):
        """::

        #: Return the enthalpy in the chamber (BTU/lbm)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        """
        return 5500.
        return hList[ 0 ] # BTU/lbm  # 0 == self.i_chm here


    def get_Densities(self, Pc=100.0, MR=1.0,eps=40.0, frozen=0, frozenAtThroat=0):
        """::

        #: Return a list of densities at the chamber, throat and exit(lbm/cuft)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen = flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        """
        return [4.,3.,2.,1.]
        return dList

    def get_Chamber_Density(self, Pc=100.0, MR=1.0, eps=40.0):
        """::

        #: Return the density in the chamber(lbm/cuft)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        """
        return 4.
        return dList[ 0 ] # lbm/cuft  # 0 == self.i_chm here


    def get_HeatCapacities(self, Pc=100.0, MR=1.0,eps=40.0, frozen=0, frozenAtThroat=0):
        """::

        #: Return a list of heat capacities at the chamber, throat and exit(BTU/lbm degR)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        """
        return [4.,3.,2.,1.]
        return cpList

    def get_Chamber_Cp(self, Pc=100.0, MR=1.0, eps=40.0, frozen=0):
        """::

        #: Return the heat capacity in the chamber(BTU/lbm degR)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen flag (0=equilibrium, 1=frozen)
        """
        return 4.
        return cpList[ 0 ] # BTU/lbm degR  # 0 == self.i_chm here

    def get_Throat_Isp(self, Pc=100.0, MR=1.0, frozen=0):
        """::

        #: Return the IspVac for the throat(sec).
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: frozen = flag (0=equilibrium, 1=frozen)
        """
        return 300.
        return IspVac


    def get_Chamber_MolWt_gamma(self, Pc=100.0, MR=1.0, eps=40.0):
        """::

        #: return the tuple (mw, gam) for the chamber (lbm/lbmole, -)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        """
        return 30., 1.3
        return mw,gam

    def get_Throat_MolWt_gamma(self, Pc=100.0, MR=1.0, eps=40.0, frozen=0):
        """::

        #: return the tuple (mw, gam) for the throat (lbm/lbmole, -)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen = flag (0=equilibrium, 1=frozen)
        """
        return 30., 1.3
        return mw,gam

    def get_exit_MolWt_gamma(self, Pc=100.0, MR=1.0, eps=40.0, frozen=0, frozenAtThroat=0):
        """::

        #: return the tuple (mw, gam) for the nozzle exit (lbm/lbmole, -)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen = flag (0=equilibrium, 1=frozen)
        #: frozenAtThroat = flag 0=frozen in chamber, 1=frozen at throat
        """
        return 30., 1.3
        return mw,gam


    def get_eqratio(self, Pc=100.0, MR=1.0, eps=40.0):
        '''Returns BOTH ERr and ERphi (valence basis and mass basis respectively)'''
        #common /miscr/ a,atwt,avgdr,boltz,b0,eqrat,...
        return 1., 1.
        return float(ERr), float(ERphi)

    def getMRforER(self, ERphi=None, ERr=None):
        """::

        #: return the value of mixture ratio that applies to the input equivalence ratio.
        #: Can be ERr or ERphi (valence basis and mass basis respectively)
        """
        return 1.3
        return float(MR)

    def get_description(self):
        """Return a string description of the propellant(s).  e.g. 'LOX / MMH'"""
        return 'Gibberish'
        return str(self.desc)

    def estimate_Ambient_Isp(self, Pc=100.0, MR=1.0, eps=40.0, Pamb=14.7, 
                             frozen=0, frozenAtThroat=0):
        """::

        #: return the tuple (IspAmb, mode)
        #: Use throat gam to run ideal separation calculations.
        #: mode is a string containing, UnderExpanded, OverExpanded, or Separated
        #: Pc = combustion end pressure (psia)
        #: Pamb ambient pressure (e.g. sea level=14.7 psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen flag, 0=equilibrium, 1=frozen 
        #: frozenAtThroat flag, 0=frozen in chamber, 1=frozen at throat
        """
        return 300., 'Gibberish'
        return IspAmb, mode


    def get_PambCf(self, Pamb=14.7, Pc=100.0, MR=1.0, eps=40.0):
        """::

        #: Return the Thrust Coefficient (CF) for equilibrium chemistry and ambient pressure
        #: Pc = combustion end pressure (psia)
        #: Pamb ambient pressure (e.g. sea level=14.7 psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        """

        return 1.6, 1.5, 'Gibberish'
        return CFcea, CFamb, mode

    def getFrozen_PambCf(self, Pamb=0.0, Pc=100.0, MR=1.0, eps=40.0, frozenAtThroat=0):
        """::

        #: Return the Thrust Coefficient (CF) for frozen chemistry and ambient pressure
        #: Pc = combustion end pressure (psia)
        #: Pamb ambient pressure (e.g. sea level=14.7 psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozenAtThroat flag, 0=frozen in chamber, 1=frozen at throat
        """
        return 1.6, 1.5, 'Gibberish'
        return CFcea,CFfrozen, mode

    def get_Chamber_Transport(self, Pc=100.0, MR=1.0, eps=40.0, frozen=0):
        """::

        #: Return a list of heat capacity, viscosity, thermal conductivity and Prandtl number
        #: in the chamber. (units are default printout units)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio... has no effect on chamber properties
        #: frozen flag (0=equilibrium, 1=frozen)
        """
        return 1.6, 1.5, 1.2, 1.0
        return Cp, visc, cond, Prandtl

    def get_Throat_Transport(self, Pc=100.0, MR=1.0, eps=40.0, frozen=0):
        """::

        #: Return a list of heat capacity, viscosity, thermal conductivity and Prandtl number
        #: in the throat. (units are default printout units)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio... has no effect on throat properties
        #: frozen flag (0=equilibrium, 1=frozen)
        """
        return 1.6, 1.5, 1.2, 1.0
        return Cp, visc, cond, Prandtl

    def get_Exit_Transport(self, Pc=100.0, MR=1.0, eps=40.0, frozen=0):
        """::

        #: Return a list of heat capacity, viscosity, thermal conductivity and Prandtl number
        #: at the exit. (units are default printout units)
        #: Pc = combustion end pressure (psia)
        #: MR is only used for ox/fuel combos.
        #: eps = Nozzle Expansion Area Ratio
        #: frozen flag (0=equilibrium, 1=frozen)
        """
        return 1.6, 1.5, 1.2, 1.0
        return Cp, visc, cond, Prandtl

