from rocketisp.unit_conv_data import get_category, get_value_str
from rocketisp.HTMLTags import TABLE, TR, TD, TH, SPAN, H3, H1
import time


def list_member_str( i, s, len_list, numbered=True, intro_str='*) '):
    if numbered:
        fmt = '%i) '
        if len_list > 9:
            fmt = '%2i) '
        return fmt%(i+1,) + s
    else:
        return intro_str + s

class Comments:
    """A collection of comments"""
    def __init__(self, comments_name='Comments'):
        self.comments_name = comments_name
        self.commentL = [] # list of comment strings
    
    def __len__(self):
        return len(self.commentL)
    
    def add_comment(self, comment):
        self.commentL.append( comment )
        
    def comment_str(self, numbered=True, add_trailer=True, fillchar='=', max_banner=70, intro_str='*) '):
        sL = []
        for i,s in enumerate(self.commentL):
            sL.append( list_member_str( i, s, len(self), numbered=numbered, intro_str=intro_str) )
        
        len_banner = min(max_banner, max([len(s) for s in sL]))
        s = (' '+self.comments_name+' ').center( len_banner, fillchar )
        sL.insert(0, s)
        
        if add_trailer:
            sL.append( fillchar*len_banner )
        return '\n'.join(sL)
        
    def html_table_str(self, numbered=True, intro_str='*) '):
        table = TABLE( width="100%")
        
        table <= TR( TH(self.comments_name, Class="h_msg", align="left") )
        
        for i,s in enumerate(self.commentL):
            n_nbs = len(s) - len( s.lstrip() )
            s = '&nbsp;'*n_nbs + s.lstrip()
            table <= TR( TD(list_member_str( i, s, len(self), numbered=numbered, intro_str=intro_str) , align="left" ) )
            
        return str( table )

class Parameter:
    """A single Parameter"""
    def __init__(self, pname, value, units='', description='', fmt='%s'):
        self.pname       = pname
        self.value       = value
        self.units       = units
        self.description = description
        try:
            self.value_str   = fmt%value
        except:
            self.value_str   = '%s'%value
            
        self.commentL    = [] # optional comments may be added later
    def add_comment(self, comment):
        self.commentL.append( str(comment) )
    def has_comments(self):
        return len(self.commentL)

DEFAULT_FMTS_D = {'':'%g',
                  'psia':'%.2f', 'MPa':'%.4f', 'atm':'%.4f', 'bar':'%.4f','psid':'%.2f',
                  'lbf':'%.1f', 'N':'%.1f',
                  'sec':'%.2f','N-sec/kg':'%.2f', 'km/sec':'%.4f',
                  'degR':'%.1f','degK':'%.1f', 'degC':'%.1f', 'degF':'%.1f', 
                  'deg':'%.2f',
                  'Hz':'%.1f', 'kHz':'%.3f',
                  'elem/in**2':'%.3f', 'elem/cm**2':'%.3f',
                  'g/gmole':'%.3f', 
                  'lbm/s':'%.3f', 'kg/s':'%.3f',
                  'lbm/inch**3':'%.5f', 'lbm/ft**3':'%.2f', 'g/ml':'%.3f',
                  'poise':'%.3e', 'cpoise':'%.5f', 'Pa*s':'%.3e', 'lbm/s/inch':'%.3e', 'lbm/hr/ft':'%.5f',
                  'lbf/in':'%.3e', 'N/m':'%.4f', 'mN/m':'%.3f', 'dyne/cm':'%.3f',
                  'ft/s':'%.1f', 'm/s':'%.1f',
                  'BTU/lbm':'%.2f', 'cal/g':'%.3f', 'kcal/g':'%.3e', 'kcal/kg':'%.3f', 'J/g':'%.3f',
                  'in':'%.3f', 'cm':'%.2f', 'ft':'%.2f', 'mil':'%.2f', 'mm':'%.3f', 'micron':'%g',
                  'in**2':'%.3f', 'cm**2':'%.1f',
                  'in**3':'%.1f', 'cm**3':'%.1f'}

def get_viable_fmt( value, units, fmtD ):
    """Check fmtD for units, if not there, make the best of it"""
    if units in fmtD:
        fmt = fmtD[units]
        try:
            s = fmt%value 
            return fmt
        except:
            fmt = '%g'

    try:
        s = fmt%value 
        return fmt
    except:
        return '%s'
            

class Parameters:
    """A collection of Parameters"""
    def __init__(self, parameters_name='Parameters'):
        self.parameters_name = parameters_name
        self.parameterL = [] # list of Parameter objects
        self.parameterD = {} # dictionary of Parmeter objects
        self.max_name_len = 1
        self.max_value_len = 1
        self.max_unit_len = 1
        self.max_desc_len = 1
        
        # specific parameter units 
        self.param_fmtD = {} # key=parameter name, value=format string
        
        # alternate units
        self.alternate_unitD = {} # key=standard units, value=list of alternate units
        self.unit_fmtD = DEFAULT_FMTS_D.copy() # key=units, value=format string
        
        self.category_setD = {} # index=category name, value=set of parameter names in category
        self.category_orderL = [] # order in which categories are entered (and output)
        self.category_allowsortD = {} # index=category name, value=flag True or False to allow alpha ordering
    
    def add_category(self, cat_name, allowsort=True):
        self.category_setD[cat_name] = set() # index=category name, value=set of parameter names in category
        self.category_orderL.append( cat_name ) # order in which categories are entered (and output)
        self.category_allowsortD[cat_name] = allowsort
        
    
    def add_param_fmt(self, pname, fmt):
        """If a specific parameter requires a specific format, set it here."""
        self.param_fmtD[ pname ] = fmt
    
    def add_alt_units(self, std_units='in', alt_units='cm', fmt=''):
        """
        alt_unitsL can be string or list of strings.
        fmtL can be string or list of strings.
        """
        alt_unitsL = alt_units
        fmtL = fmt
        # convert string inputs into lists
        if type(alt_unitsL)==type('string'):
            alt_unitsL = [ alt_unitsL ]
        if type(fmtL)==type('string'):
            fmtL = [fmtL] * len(alt_unitsL)
        while len(fmtL) < len(alt_unitsL): # make sure len of fmtL is at least alt_unitsL
            fmtL.append( fmtL[-1] )
                
        
        if std_units in self.alternate_unitD:
            self.alternate_unitD[ std_units ].extend( alt_unitsL )
        else:
            self.alternate_unitD[ std_units ] = alt_unitsL[:] # make copy of input list
        
            
        # now that lists are created, check for default unit formats
        for alt_units, fmt in zip(alt_unitsL, fmtL):
            if fmt!='' and alt_units in self.unit_fmtD:# alter format of alt_units from the DEFAULT_FMTS_D
                print('Changing alt_units for %s from "%s" to "%s"'%\
                      (alt_units, self.unit_fmtD[ alt_units ], fmt))
                self.unit_fmtD[ alt_units ] = fmt
                
    def get_alt_units_str(self, pname):
        sL = []
        if pname in self.parameterD: 
            p = self.parameterD[ pname ]
            if p.value is not None:
                if p.units in self.alternate_unitD:
                    for alt_units in self.alternate_unitD[p.units]:
                        if 1:#try:
                            # get string with formated value and units (e.g. "1.234 cm")
                            fmt = get_viable_fmt( p.value, p.units, self.unit_fmtD )
                            s = get_value_str( p.value, p.units, alt_units, fmt=fmt )
                            sL.append( s )
                        else:#except:
                            sL.append( '??? %s'%alt_units )
        return  ', '.join(sL)
    
    def __len__(self):
        return len(self.parameterL)
    
    def add_parameter(self, pname, value, units='', description='', fmt='', category=''):
        
        # add pname to self.category_setD
        if category not in self.category_setD:
            self.category_setD[ category ] = set()
            self.category_orderL.append( category )
        self.category_setD[ category ].add( pname )
        
        if fmt:
            self.param_fmtD[ pname ] = fmt # just use input value
        if pname in self.param_fmtD:
            fmt = self.param_fmtD[ pname ]
        elif units in self.unit_fmtD:
            fmt = self.unit_fmtD[units]
        elif type(value) == type(1.234):
            fmt = '%g'
        else:
            fmt = "%s"
        
        if pname in self.parameterD:
            # potential problem for duplicate additions
            p = self.parameterD[ pname ]
            p.add_comment( '--> %s, %s, %s'%(value, units, description) )
        else:
            p = Parameter(pname, value, units=units, description=description, fmt=fmt)
            self.parameterD[ pname ] = p
            self.parameterL.append( p )
            
        self.max_name_len  = max( len(pname), self.max_name_len )
        self.max_unit_len  = max( len(units), self.max_unit_len )
        
        self.max_value_len = max( len(p.value_str), self.max_value_len)
        
        self.max_desc_len  = max( len(description), self.max_desc_len)
        
        return p
        
    def add_comment(self, pname, comment):
        self.parameterD[ pname ].add_comment( comment )

    def summ_str(self, alpha_ordered=True, numbered=True, add_trailer=True, 
                 fillchar='=', max_banner=70, intro_str='*) '):
        
        # figure out format statement to align columns
        fmt_pname   = '%' + '%is = '%self.max_name_len
        fmt_pname_2 = '%' + '%is   '%self.max_name_len
        
        fmt_units = '%' + '%is '%self.max_unit_len
        fmt_value = '%' + '%is '%self.max_value_len
                
        # perhaps put items in alphabetical order
        if alpha_ordered:
            pL = sorted([(p.pname.lower(), p) for p in self.parameterL])
            pL = [p for (_,p) in pL]
        else:
            pL = self.parameterL
        
        # build string list that will be concatenated with '\n'
        sL = []
        for cat_name in self.category_orderL:
            if cat_name:
                sL.append( '..%s..'%cat_name )
            allowsort = self.category_allowsortD.get(cat_name, True)
            if allowsort:
                plist = pL
            else:
                plist = self.parameterL
                
            for i,p in enumerate(plist):
                if p.pname in self.category_setD[ cat_name ]:
                
                    s = fmt_pname%p.pname + fmt_value%p.value_str + fmt_units%p.units  +' '+ p.description
                    sL.append( list_member_str( i, s, len(self), numbered=numbered, intro_str=intro_str) )
                    
                    saltu = self.get_alt_units_str( p.pname )
                    if saltu:
                        saltu = '(%s)'%saltu
                        
                        # add alternate units as a second line
                        s = fmt_pname_2%'' + fmt_value%'' + fmt_units%''  +' '+ saltu
                        sL.append( list_member_str( i, s, len(self), numbered=numbered, intro_str=intro_str) )
                    
                    if p.has_comments():
                        pad = ' '*len(list_member_str( i, '', len(self), numbered=numbered, intro_str=intro_str))
                        pad += fmt_pname_2%' ' + fmt_value%' ' + fmt_units%' ' +' '
                        for c in p.commentL:
                            sL.append( pad + '(%s)'%c )
            
        # add banner(s) at top and perhaps bottom
        len_banner = min(max_banner, max([len(s) for s in sL]))
        s = (' '+self.parameters_name+' ').center( len_banner, fillchar )
        if len(s) < max_banner:
            n = max_banner - len(s)
            s = s + fillchar*n
        sL.insert(0, s)
        
        if add_trailer:
            sL.append( fillchar*max_banner )
        
        return '\n'.join(sL)
        
    def has_alt_units(self):
        for p in self.parameterL:
            if self.get_alt_units_str( p.pname ):
                return True
        return False
    
    def html_table_str(self, alpha_ordered=True, numbered=False, intro_str=''):
        
        has_alt_units = self.has_alt_units()
        if has_alt_units:
            colspan_str = "3"
        else:
            colspan_str = "2"
        
        table = TABLE( width="100%")
        table <= TR( TH( self.parameters_name, align="center", Class="h_msg", colspan=colspan_str ) )

        # perhaps put items in alphabetical order
        if alpha_ordered:
            pL = sorted([(p.pname.lower(), p) for p in self.parameterL])
            pL = [p for (_,p) in pL]
        else:
            pL = self.parameterL
        
        for cat_name in self.category_orderL:
            allowsort = self.category_allowsortD.get(cat_name, True)
            if allowsort:
                plist = pL
            else:
                plist = self.parameterL
                
            # build string lists, one for each column
            name_sL = []
            value_sL = []
            alt_value_sL = []
            
            descL = []
                
            for i,p in enumerate(plist):
                if p.pname in self.category_setD[ cat_name ]:
                    name_sL.append( p.pname )
                    value_sL.append( p.value_str + ' ' + p.units )
                    descL.append( p.description )
                
                    saltu = self.get_alt_units_str( p.pname )
                    if saltu:
                        saltu = saltu.replace(', ','<BR>')
                        alt_value_sL.append( saltu )
                    else:
                        alt_value_sL.append( '' )
                    
                    if p.has_comments():
                        for c in p.commentL:
                            descL[-1] = descL[-1] + '<BR>' + c
            
            if cat_name:
                table <= TR( TH( cat_name, align="left", colspan=colspan_str, Class="h_msg" ))
                
            if has_alt_units:
                table <= TR( TH('Parameter =', align="right", width="20%" ) + TH('Value', align="left") +\
                             TH('Alt Value', align="left") +TH('Description', align="left"))
            else:
                table <= TR( TH('Parameter =', align="right", width="20%") +TH('Value', align="left") +TH('Description', align="left"))
            
            for name, val, alt, desc in zip(name_sL, value_sL, alt_value_sL, descL):
                TD1 = TD( name + ' =', align="right", Class="isp_data"  )
                TD2 = TD( val, align="left", nowrap="true", Class="isp_data" )
                TD4 = TD( desc, align="left", Class="desc_data" )
                
                if has_alt_units:
                    TD3 = TD( alt, nowrap="true", Class="alt_data"  )
                    table <= TR(TD1 + TD2 + TD3 + TD4 )
                else:
                    table <= TR(TD1 + TD2 + TD4 )

        return str( table )


class ModelSummary:
    
    def __init__(self, name='Generic Model', title_assumptions='Assumptions'):
        
        self.name = name
        self.assumptions = Comments(title_assumptions)
        #self.inp_parameters = Parameters(name +' Input')
        #self.out_parameters = Parameters(name +' Output')
        self.inp_parameters = Parameters(' Input')
        self.out_parameters = Parameters(' Output')
        
        self.warnings = Comments('Warnings')
    
    def add_alt_units(self, std_units='in', alt_units='cm', fmt=''):
        self.inp_parameters.add_alt_units( std_units=std_units, alt_units=alt_units, fmt=fmt )
        self.out_parameters.add_alt_units( std_units=std_units, alt_units=alt_units, fmt=fmt )
    
    def add_assumption(self, s ):
        self.assumptions.add_comment( s )
        
    def add_warning(self, s ):
        self.warnings.add_comment( s )
        
    def add_param_fmt(self, pname, fmt):
        self.inp_parameters.add_param_fmt( pname, fmt)
        self.out_parameters.add_param_fmt( pname, fmt)
    
    def add_inp_category(self, cat_name, allowsort=True):
        self.inp_parameters.add_category( cat_name, allowsort=allowsort )
    
    def add_inp_param(self, pname, value, units='', description='', fmt='', category=''):
        self.inp_parameters.add_parameter( pname=pname, value=value, units=units, 
                                           description=description, fmt=fmt, category=category )
    
    def add_inp_comment(self, pname, comment):
        self.inp_parameters.add_comment( pname, comment )
    
    def add_out_category(self, cat_name, allowsort=True):
        self.out_parameters.add_category( cat_name, allowsort=allowsort )
    
    def add_out_param(self, pname, value, units='', description='', fmt='', category=''):
        self.out_parameters.add_parameter( pname=pname, value=value, units=units, 
                                           description=description, fmt=fmt, category=category )
    
    def add_out_comment(self, pname, comment):
        self.out_parameters.add_comment( pname, comment )
        
    def summ_str( self, alpha_ordered=True, numbered=False, add_trailer=True, 
                  fillchar='=', max_banner=70, intro_str='', assumptions_first=True ):
                      
        s = (' '+self.name+' ').center( max_banner, fillchar )
        sL = [s]
        
        if assumptions_first and len(self.assumptions):
            sL.append( self.assumptions.comment_str(numbered=numbered, add_trailer=True, 
                                                    fillchar=fillchar, max_banner=max_banner, 
                                                    intro_str=intro_str) )
        if len(self.warnings):
            sL.append( self.warnings.comment_str(numbered=numbered, add_trailer=True, 
                                                 fillchar=fillchar, max_banner=max_banner, 
                                                 intro_str=intro_str) )
        if len(self.inp_parameters):
            sL.append( self.inp_parameters.summ_str(alpha_ordered=alpha_ordered, 
                                                numbered=numbered, add_trailer=add_trailer, 
                                                fillchar=fillchar, max_banner=max_banner, 
                                                intro_str=intro_str) )
        if len(self.out_parameters):
            sL.append( self.out_parameters.summ_str(alpha_ordered=alpha_ordered, 
                                                numbered=numbered, add_trailer=add_trailer, 
                                                fillchar=fillchar, max_banner=max_banner, 
                                                intro_str=intro_str) )
                                                
        if not assumptions_first and len(self.assumptions):
            sL.append( self.assumptions.comment_str(numbered=numbered, add_trailer=True, 
                                                    fillchar=fillchar, max_banner=max_banner, 
                                                    intro_str=intro_str) )
        
        return '\n'.join(sL)
        
    def html_table_str(self, alpha_ordered=True, numbered=False, intro_str='', assumptions_first=True):
        
        table = TABLE( width="100%")
        table <= TR( TH( self.name, align="center", Class="h_msg") )
        sL = [ str(table) ]

        
        if assumptions_first and len(self.assumptions):
            sL.append( str( self.assumptions.html_table_str(numbered=numbered, intro_str=intro_str) ) )
            
        if len(self.warnings):
            sL.append( str( self.warnings.html_table_str(numbered=numbered, intro_str=intro_str) ) )
            
        if len(self.inp_parameters):
            sL.append( str( self.inp_parameters.html_table_str(alpha_ordered=alpha_ordered, numbered=numbered, intro_str=intro_str) ) )
            
        if len(self.out_parameters):
            sL.append( str( self.out_parameters.html_table_str(alpha_ordered=alpha_ordered, numbered=numbered, intro_str=intro_str) ) )
                                                
        if not assumptions_first and len(self.assumptions):
            sL.append( str( self.assumptions.html_table_str(numbered=numbered, intro_str=intro_str) ) )
        
        return '\n'.join( sL )
        

if __name__ == "__main__":
    from rocketisp.geometry import Geometry
    from rocketisp.parse_docstring import get_desc_and_units

    
    M = ModelSummary('What Model')
    
    descD, unitsD, is_inputD = get_desc_and_units( Geometry.__doc__ )
    geomObj = Geometry()
    for pname, desc in descD.items():
        M.add_inp_param( pname, getattr(geomObj,pname), unitsD[pname], desc)
        
    M.add_alt_units('deg', 'rad', fmt='%.4f')
    M.add_alt_units('in', 'cm')
    M.add_alt_units('degR', 'degC')
    M.add_alt_units('psia', 'atm')
    M.add_alt_units('Hz', 'kHz')
    
    print( M.summ_str() )
    
