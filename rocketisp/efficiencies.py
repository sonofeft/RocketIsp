
class Efficiency:
    """
    Holds an individual efficiency that is coordinated by the Efficiencies object.

    :param name: name of efficiency (e.g. Div, BL, Kin, etc)
    :param value: initial value of efficiency (should be between 0.0 and 1.0)
    :param desc: long description of efficiency
    :param value_src: technical source of the efficiency (e.g. user input, NASA model, etc.)
    :type name: str
    :type value: float
    :type desc: str
    :type value_src: str
    :return: Efficiency object
    :rtype: Efficiency    
    """
    def __init__(self, name, value, desc, value_src):
        
        self.name      = name
        self.value     = value
        self.desc      = desc
        self.value_src = value_src
        self.is_const  = False
    
    def set_const(self, value):
        self.value     = value
        self.value_src = 'constant'
        self.is_const  = True
        
    def set_value(self, value, value_src):
        """
        Every time a new value is set, the source of that value must be given.
        """
        self.value     = value
        self.value_src = value_src
        
class Efficiencies:
    """
    Holds all of the thrust chamber efficiencies and provides access to 
    efficiency models in order to update each one.
    """
    
    def __init__(self, **constD):
        
        self.effD  = {} # index=eff name, value=Efficiency object
        
        # individual mechanism efficiencies
        self.effD['Div']   = Efficiency('Div', 1.0, 'Divergence Efficiency of Nozzle', 'default')
        self.effD['Kin']   = Efficiency('Kin', 1.0, 'Kinetic Efficiency of Nozzle', 'default')
        self.effD['BL']    = Efficiency('BL', 1.0, 'Boundary Layer Efficiency of Nozzle', 'default')
        self.effD['TP']    = Efficiency('TP', 1.0, 'Two Phase Efficiency of Nozzle', 'default')
        self.effD['Mix']   = Efficiency('Mix', 1.0, 'Inter-Element Mixing Efficiency of Injector', 'default')
        self.effD['Em']    = Efficiency('Em', 1.0, 'Intra-Element Mixing Efficiency of Injector', 'default')
        self.effD['Vap']   = Efficiency('Vap', 1.0, 'Vaporization Efficiency of Injector', 'default')
        self.effD['HL']    = Efficiency('HL', 1.0, 'Heat Loss Efficiency of Chamber', 'default')
        self.effD['FFC']   = Efficiency('FFC', 1.0, 'Fuel Film Cooling Efficiency of Chamber', 'default')
        self.effD['Pulse'] = Efficiency('Pulse', 1.0, 'Pulsing Efficiency of Thruster', 'default')
        
        self.nozzleL = ['Div','Kin','BL','TP']
        self.chamberL = ['Mix','Em','Vap','HL']
        self.toplevelL = ['Isp','IspPulsing']

        # consolidated efficiencies (product of selected individual efficiencies)
        self.effD['ERE']        = Efficiency('ERE', 1.0, 'Energy Release Efficiency', '')
        self.effD['Noz']        = Efficiency('Noz', 1.0, 'Nozzle Efficiency', '')
        self.effD['Isp']        = Efficiency('Isp', 1.0, 'Overall Isp Efficiency', '')
        self.effD['IspPulsing'] = Efficiency('IspPulsing', 1.0, 'Pulsing Isp Efficiency', '')
        
        for name, value in constD.items():
            if name in self.effD:
                self.set_const( name, value, re_evaluate=True)
            else:
                raise Exception('in Efficiencies, "%s" is not recognized as an efficiency'%name)
        
    
    def __getitem__(self, name):
        return self.effD[name]
        
    def __call__(self, name):
        return self.effD[name].value
    
    def set_const(self, name, value, re_evaluate=True):
        """
        Give a new constant value to named efficiency. Call evaluate if re_evaluate is True.
        """
        self.effD[name].set_const( value )
        if re_evaluate:
            self.evaluate()        
    
    def set_value(self, name, value, value_src='user input', re_evaluate=True):
        """
        Give a new value to named efficiency. Call evaluate if re_evaluate is True.
        """
        self.effD[name].set_value( value, value_src )
        if re_evaluate:
            self.evaluate()
        
    
    def evaluate(self):
        """
        Combines nozzle and chamber efficiencies into overall nozzle and 
        over chamber efficiency.
        Gives overall Isp efficiency including any pulsing effects.
        """
        if not self.effD['Isp'].is_const:
            enoz = self['Noz']
            if enoz.is_const:
                effNoz = enoz.value
            else:
                effNoz = 1.0
                for name in self.nozzleL: # ['Div','Kin','BL','TP']
                    e = self.effD[name]
                    effNoz *= e.value
                enoz.set_value( effNoz, '' )

            eere = self['ERE']
            if eere.is_const:
                effERE = eere.value
            else:
                effERE = 1.0
                for name in self.chamberL: #  ['Mix','Em','Vap','HL']
                    e = self.effD[name]
                    effERE *= e.value
                self.effD['ERE'].set_value( effERE, '' )
            
            self.effD['Isp'].set_value( effERE * effNoz * self.effD['FFC'].value, '' )
        
        if not self.effD['IspPulsing'].is_const:
            self.effD['IspPulsing'].set_value( self.effD['Isp'].value * self.effD['Pulse'].value, 
                                               self['Pulse'].value_src )

        
    def summ_print(self):
        """
        print to standard output, the current state of Efficiencies instance.
        """
        
        print('%s Thruster Efficiencies %s'%('='*12,'='*12))
        
        # top level efficiencies
        e = self['Isp']
        print('%s  %.5f'%(' '*12,e.value), '%s'%( e.desc, )  )
        
        if self.effD['Pulse'].value < 1.0:
            e = self['IspPulsing']
            print('%s  %.5f'%(' '*12,e.value), '%s (%s)'%( e.desc, e.value_src)  )

        if not self.effD['Isp'].is_const:
            # nozzle
            #print()
            e = self.effD['Noz']
            if e.value_src: 
                msg='(%s) '%e.value_src
            else:
                msg=''
                
            print('%s  %.5f'%('-'*12,e.value), '%sNozzle Efficiency %s'%(msg,'-'*12,)  )
            if not e.is_const:
                for name in self.nozzleL:
                    e = self.effD[name]
                    print(' %10s ='%name, '%.5f'%e.value, '(%s)'%e.value_src, e.desc)

            # ERE
            #print()
            e = self.effD['ERE']
            if e.value_src: 
                msg='(%s) '%e.value_src
            else:
                msg=''
                
            print('%s  %.5f'%('-'*12,e.value), '%sEnergy Release Efficiency %s'%(msg,'-'*12,)  )
            if not e.is_const:
                for name in self.chamberL:
                    e = self.effD[name]
                    print(' %10s ='%name, '%.5f'%e.value, '(%s)'%e.value_src, e.desc)
            
        # Fuel Film Cooling
        e = self.effD['FFC']
        if e.value < 1.0:
            print()
            print('%s  %.5f'%('-'*12,e.value), 'Fuel Film Cooling %s'%('-'*12,)  )
        
        # Pulsing
        e = self.effD['Pulse']
        if e.value < 1.0:
            print()
            print('%s  %.5f'%('-'*12,e.value), 'Pulsing Efficiency %s'%('-'*12,)  )
        

if __name__ == '__main__':
    
    E = Efficiencies()
    E.set_const('Div', .9 )
    E.set_const('Mix', .89 )
    #E.set_const('Noz', .95 )
    #E.set_const('ERE', .97 )
    E.summ_print()
    print( 'E("Mix") =', E("Mix") )
    print('='*66)
    E.set_value('Em', 0.99)
    E.set_value('Pulse', 0.99)
    E.summ_print()
    