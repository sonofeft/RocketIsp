from math import sqrt
from rocketisp.model_summ import ModelSummary

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
        """
        Initialize an efficiency object
        """
        
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
        
    def get_state_str(self):
        """Return a | delimited state string."""
        return '%s|%s|%s|%s|%s'%(self.name, self.value, self.desc, self.value_src, self.is_const)
        
class Efficiencies:
    """
    Holds all of the thrust chamber efficiencies and provides access to 
    efficiency models in order to update each one.
    """
    
    def set_to_default(self):
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
        
        # consolidated efficiencies (product of selected individual efficiencies)
        self.effD['ERE']        = Efficiency('ERE', 1.0, 'Energy Release Efficiency of Chamber', '')
        self.effD['Noz']        = Efficiency('Noz', 1.0, 'Nozzle Efficiency', '')
        self.effD['Isp']        = Efficiency('Isp', 1.0, 'Overall Isp Efficiency', '')
        self.effD['IspPulsing'] = Efficiency('IspPulsing', 1.0, 'Pulsing Isp Efficiency', '')
    
    def __init__(self, **constD):
        
        self.effD  = {} # index=eff name, value=Efficiency object
        
        self.nozzleL = ['Div','Kin','BL','TP']
        self.chamberL = ['Mix','Em','Vap','HL']
        self.toplevelL = ['Isp','IspPulsing']
        
        self.set_to_default()

        # if individual efficiency is input, consider it constant.
        for name, value in constD.items():
            if name in self.effD:
                self.set_const( name, value, re_evaluate=True)
            else:
                raise Exception('in Efficiencies, "%s" is not recognized as an efficiency'%name)
                
    def get_state_str_list(self):
        """Return a list of | delimited state strings for each Efficiency"""
        return [e.get_state_str() for e in self.effD.values()]
    
    def __getitem__(self, name):
        return self.effD[name]
        
    def __call__(self, name):
        return self.effD[name].value
    
    def set_const(self, name, value, re_evaluate=True):
        """
        Give a new constant value to named efficiency. Call evaluate if re_evaluate is True.
        """
        self.effD[name].set_const( value )
        # if setting effIsp, then split it between ERE and Noz 
        if name == 'Isp':
            self.effD['ERE'].set_const( sqrt(value) )
            self.effD['Noz'].set_const( sqrt(value) )
            
        
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
        print( self.get_summ_str() )
        
    def get_summ_str(self):
        
        """
        return string of the current state of Efficiencies instance.
        """
        M = self.get_model_summ_obj()
        return M.summ_str(alpha_ordered=False, fillchar='.', assumptions_first=False)
    
    def get_html_str(self, alpha_ordered=True, numbered=False, intro_str=''):
        M = self.get_model_summ_obj()
        return M.html_table_str( alpha_ordered=alpha_ordered, numbered=numbered, intro_str=intro_str)
        
    def get_model_summ_obj(self):
        """
        return ModelSummary object for current state of Efficiencies instance.
        """
        
        M = ModelSummary( 'Efficiencies', title_assumptions='Ignored Efficiencies' )
        
        M.add_out_category( '' ) # show unlabeled category 1st
        M.add_inp_category( '' ) # show unlabeled category 1st
            
        # dpOx dpFuel
        def get_cat( name ):
            if name in self.nozzleL:# = ['Div','Kin','BL','TP']
                return 'Nozzle'
            if name in self.chamberL:# =  ['Mix','Em','Vap','HL']
                return 'Chamber'
            return ''
        
        # -----------------------------------------------
        def add_inp( name ):
            if self.effD[name].value_src:
                s = '(%s)'%self.effD[name].value_src + ' ' + self.effD[name].desc
            else:
                s = self.effD[name].desc
            M.add_inp_param( name, self.effD[name].value, units='', 
                             description=s, fmt='%.5f', category=get_cat(name))
        def add_out( name ):
            if self.effD[name].value_src:
                s = '(%s)'%self.effD[name].value_src + ' ' + self.effD[name].desc
            else:
                s = self.effD[name].desc
            M.add_out_param( name, self.effD[name].value, units='', 
                             description=s, fmt='%.5f', category=get_cat(name))

        def add_as_appropriate( name ):
            if self.effD[name].value_src == 'default':
                M.add_assumption( '        %s: '%name + self.effD[name].desc )
            elif self.effD[name].is_const:
                add_inp( name )
            else:
                add_out( name )
                
        add_out( 'Isp' )
        
        if self.effD['Pulse'].value < 1.0:
            add_out( 'IspPulsing' )
        
        if not self.effD['Isp'].is_const:
            # nozzle
            add_out( 'Noz' )
            if not self.effD['Isp'].is_const:
                for name in self.nozzleL:
                    add_as_appropriate( name )
            
            add_out( 'ERE' )
            if not self.effD['ERE'].is_const:
                for name in self.chamberL:
                    add_as_appropriate( name )
            
        # Fuel Film Cooling
        if self.effD['FFC'].value < 1.0:
            add_out( 'FFC' )
        
        # Pulsing
        if self.effD['Pulse'].value < 1.0:
            add_out( 'Pulse' )
        
        
        return M

if __name__ == '__main__':
    import sys
    
    E = Efficiencies()
    E.set_const('Div', .9 )
    E.set_const('Mix', .89 )
    #E.set_const('Noz', .95 )
    #E.set_const('ERE', .97 )
    
    #M = E.get_model_summ_obj()
    #print( M.summ_str(alpha_ordered=False) )
    
    #print('<>'*44)
    E.summ_print()
    
    print( 'E("Mix") =', E("Mix") )
    print('='*66)
    E.set_value('Em', 0.99)
    E.set_value('Pulse', 0.99)
    E.summ_print()
    
    for s in E.get_state_str_list():
        print( s )
        
    print('='*66)
    E = Efficiencies()
    contents = E.summ_print()
    print('cccccccccccccccccccccccccccccccccccc')
    print(contents)
    
    