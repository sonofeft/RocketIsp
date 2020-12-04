# -*- coding: iso-8859-1 -*-

"""Classes to generate HTML in Python

The HTMLTags module defines a class for all the valid HTML tags, written in
uppercase letters. To create a piece of HTML, the general syntax is :
    t = TAG(content, key1=val1,key2=val2,...)

so that "print t" results in :
    <TAG key1="val1" key2="val2" ...>content</TAG>

For instance :
    print A('bar', href="foo") ==> <A href="foo">bar</A>

To generate HTML attributes without value, give them the value True :
    print OPTION('foo',SELECTED=True,value=5) ==> 
            <OPTION value="5" SELECTED>

The content argument can be an instance of an HTML class, so that 
you can nest tags, like this :
    print B(I('foo')) ==> <B><I>foo</I></B>

TAG instances support addition :
    print B('bar')+INPUT(name="bar") ==> <B>bar</B><INPUT name="bar">

and repetition :
    print TH('&nbsp')*3 ==> <TD>&nbsp;</TD><TD>&nbsp;</TD><TD>&nbsp;</TD>

For complex expressions, a tag can be nested in another using the operator <= 
Considering the HTML document as a tree, this means "add child" :

    form = FORM(action="foo")
    form <= INPUT(name="bar")
    form <= INPUT(Type="submit",value="Ok")

If you have a list (or any iterable) of instances, you can't concatenate the 
items with sum(instance_list) because sum takes only numbers as arguments. So 
there is a function called Sum() which will do the same :

    Sum( TR(TD(i)+TD(i*i)) for i in range(100) )

generates the rows of a table showing the squares of integers from 0 to 99

A simple document can be produced by :
    print HTML( HEAD(TITLE('Test document')) +
        BODY(H1('This is a test document')+
             'First line'+BR()+
             'Second line'))

If the document is more complex it is more readable to create the elements 
first, then to print the whole result in one instruction. For example :

head = HEAD()
head <= TITLE('Record collection')
head <= LINK(rel="Stylesheet",href="doc.css")

title = H1('My record collection')
table = TABLE()
table <= TR(TH('Title')+TH('Artist'))
for rec in records:
    row = TR()
    # note the attribute key Class with leading uppercase 
    # because "class" is a Python keyword
    row <= TD(rec.title,Class="title")+TD(rec.artist,Class="artist")
    table <= row

print HTML(head+BODY(title+table))

"""
import sys
import io
from functools import reduce


def to_unicode(data):
    return str(data)
    #return data

class TAG:
    """Generic class for tags"""
    def __init__(self, *content, **attrs):
        self.tag = self.__class__.__name__
        self.attrs = attrs
        self.brothers = []
        # we can't init with argument content='' because of conflict
        # if a key 'content' is in **attrs
        if not content:
            self.children = []
        elif len(content)>1:
            raise ValueError('%s takes only one positional argument' %self.tag)
        else:
            self.children = [content[0]]

    def __str__(self):
        import sys
        res=io.StringIO()
        w=res.write
        if self.tag != "TEXT":
            w("<%s" %self.tag)
            # attributes which will produce arg = "val"
            attr1 = [ k for k in self.attrs 
                if not isinstance(self.attrs[k],bool) ]
            attr_list = []
            for k in attr1:
                key = k.replace('_','-')
                value = self.attrs[k]
                if isinstance(value,str):
                    value = to_unicode(value)
                attr_list.append(' %s="%s"' %(key,value))
            w("".join(attr_list))
            # attributes with no argument
            # if value is False, don't generate anything
            attr2 = [ k for k in self.attrs if self.attrs[k] is True ]
            w("".join([' %s' %k for k in attr2]))
            w(">")
        if self.tag in _ONE_LINE:
            w('\n')
        for child in self.children:
            if isinstance(child,str):
                #print('\nchild="%s", str="%s"'%(child,str) )
                #print('type(child)="%s",type(str)="%s"'%(type(child),type(str)))
                w(to_unicode(child))
            else:
                w('%s' % child)
        if self.tag in _CLOSING_TAGS:
            w("</%s>" %self.tag)
        if self.tag in _LINE_BREAK_AFTER:
            w('\n')
        for brother in self.brothers:
            w(str(brother))
            
        #print('res.getvalue(), type=', type(res.getvalue()))
        return str(res.getvalue())
    
    def __le__(self,other):
        """Add a child"""
        if isinstance(other,str):
            other = TEXT(other)
        self.children.append(other)
        other.parent = self
        return self

    def __add__(self,other):
        """Return a new instance : concatenation of self and another tag"""
        res = TAG()
        res.tag = self.tag
        res.attrs = self.attrs
        res.children = self.children
        if isinstance(other,str):
            other = TEXT(other)
        res.brothers = self.brothers + [other]
        return res

    def __radd__(self,other):
        """Used to add a tag to a string"""
        if isinstance(other,str):
            return TEXT(other)+self
        else:
            raise ValueError("Can't concatenate %s and instance" %other)

    def __mul__(self,n):
        """Replicate self n times, with tag first : TAG * n"""
        res = TAG()
        res.tag = self.tag
        res.attrs = self.attrs
        res.children = self.children
        res.brothers = self.brothers
        for i in range(n-1):
            res += self
        return res

    def __rmul__(self,n):
        """Replicate self n times, with n first : n * TAG"""
        return self*n

    def get_by_attr(self,**kw):
        """Return a list of tags whose attributes are in kw,
        at the same level as self or below in the tree"""
        res = []
        flag = True
        for k,v in kw.items():
            if self.attrs.get(k,None) !=v:
                flag = False
                break
        if flag:
            res.append(self)
        for brother in self.brothers:
            if isinstance(brother,TAG):
                res += brother.get_by_attr(**kw)
        for child in self.children:
            if isinstance(child,TAG):
                res += child.get_by_attr(**kw)
        return _tag_list(res)

    def get_by_tag(self,tag_name):
        """Return a list of tags of specified tag name,
        at the same level as self or below in the tree"""
        res = []
        if self.tag == tag_name:
            res.append(self)
        for brother in self.brothers:
            if isinstance(brother,TAG):
                res += brother.get_by_tag(tag_name)
        for child in self.children:
            if isinstance(child,TAG):
                res += child.get_by_tag(tag_name)
                for brother in child.brothers:
                    if isinstance(brother,TAG):
                        res += brother.get_by_tag(tag_name)
        return _tag_list(res)

class _tag_list(list):

    def set_attr(self,**kw):
        for item in self:
            for key,value in kw.items():
                item.attrs[key] = value

# list of tags, from the HTML 4.01 specification

_CLOSING_TAGS =  ['A', 'ABBR', 'ACRONYM', 'ADDRESS', 'APPLET',
            'B', 'BDO', 'BIG', 'BLOCKQUOTE', 'BUTTON',
            'CAPTION', 'CENTER', 'CITE', 'CODE',
            'DEL', 'DFN', 'DIR', 'DIV', 'DL',
            'EM', 'FIELDSET', 'FONT', 'FORM', 'FRAMESET',
            'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
            'I', 'IFRAME', 'INS', 'KBD', 'LABEL', 'LEGEND',
            'MAP', 'MENU', 'NOFRAMES', 'NOSCRIPT', 'OBJECT',
            'OL', 'OPTGROUP', 'PRE', 'Q', 'S', 'SAMP',
            'SCRIPT', 'SMALL', 'SPAN', 'STRIKE',
            'STRONG', 'STYLE', 'SUB', 'SUP', 'TABLE',
            'TEXTAREA', 'TITLE', 'TT', 'U', 'UL',
            'VAR', 'BODY', 'COLGROUP', 'DD', 'DT', 'HEAD',
            'HTML', 'LI', 'P', 'TBODY','OPTION', 
            'TD', 'TFOOT', 'TH', 'THEAD', 'TR']

_NON_CLOSING_TAGS = ['AREA', 'BASE', 'BASEFONT', 'BR', 'COL', 'FRAME',
            'HR', 'IMG', 'INPUT', 'ISINDEX', 'LINK',
            'META', 'PARAM']

# create the classes
for _tag in _CLOSING_TAGS + _NON_CLOSING_TAGS + ['TEXT']:
    exec("class %s(TAG): pass" %_tag)

# Convenience methods for SELECT tags, radio and checkbox INPUT tags

def _check_args(**kw):
    # check if arguments are valid for selection or check methods
    if not kw:
        raise ValueError('No arguments provided')
    elif len(list(kw.keys()))>1:
        msg = 'Function takes 1 argument, %s provided'
        raise ValueError(msg %len(list(kw.keys())))
    elif list(kw.keys())[0] not in ['content','value']:
        msg ='Bad argument %s, must be "content" or "value"'
        raise ValueError(msg %list(kw.keys())[0])
    return list(kw.keys())[0],list(kw.values())[0]

# SELECT has special methods to build a list of OPTION tags from
# a list, and marks one of several OPTION tags as selected
_CLOSING_TAGS.append('SELECT')

class SELECT(TAG):

    def from_list(self,_list,use_content=False):
    # build a SELECT tag from a list
        if not use_content:
            # values are content's rank
            self.children = [OPTION(item,value=i,SELECTED=False) 
                for (i,item) in enumerate(_list)]
        else:
            # values are content's value
            self.children = [OPTION(item,value=item,SELECTED=False) 
                for item in _list]
        return self

    def select(self,**kw):
    # mark an option (or several options if attribute MULTIPLE is set) as selected
        key,attr = _check_args(**kw)
        if not isinstance(attr,(list,tuple)):
            attr = [attr]
        if key == 'content':
            for option in self.children:
                option.attrs['SELECTED'] = option.children[0] in attr
        elif key == 'value':
            for option in self.children:
                option.attrs['SELECTED'] = option.attrs['value'] in attr

# Classes to build a list of radio and checkbox INPUT tags from a list
# of strings. All INPUT tags have the same attributes, including name
# and except the value, which is the string index in the list

# Instances of RADIO and CHECKBOX have a check() method, used to mark
# INPUT tags as checked. The argument can be a string value (or a list
# of strings) to check the tags associated with one of the items in the
# list, or an index (or a list of indices)

class RADIO:

    def __init__(self,_list,_values=None,**attrs):
        self._list = _list
        if _values is None :
            self.tags = [INPUT(Type="radio",value=i,checked=False,**attrs)
                    for i in range(len(_list))]
        else:
            if not isinstance(_values, (list, tuple)) :
                raise TypeError("_values must be a list or a tuple")
            if len(_list) != len(_values) :
                raise ValueError("len(_list) != len(_values)")
            self.tags = [INPUT(Type="radio",value=i,checked=False,**attrs)
                    for i in _values]

    def check(self,**kw):
        key,attr = _check_args(**kw)
        if key == 'content':
            for i,item in enumerate(self._list):
                self.tags[i].attrs['checked'] = self._list[i] == attr
        else:
            for (i,tag) in enumerate(self.tags):
                self.tags[i].attrs['checked'] = tag.attrs['value'] == attr

    def __iter__(self):
        return iter(zip(self._list,self.tags))

class CHECKBOX:

    def __init__(self,_list,_values=None,**attrs):
        self._list = _list
        if _values is None :
            self.tags = [INPUT(Type="checkbox",value=i,checked=False,**attrs)
                    for i in range(len(_list))]
        else:
            if not isinstance(_values, (list, tuple)) :
                raise TypeError("_values must be a list or a tuple")
            if len(_list) != len(_values) :
                raise ValueError("len(_list) != len(_values)")
            self.tags = [INPUT(Type="checkbox",value=i,checked=False,**attrs)
                    for i in _values]
            

    def check(self,**kw):
        key,attr = _check_args(**kw)
        if not isinstance(attr,(tuple,list)):
            attr = [attr]
        if key == 'content':
            for i,item in enumerate(self._list):
                self.tags[i].attrs['checked'] = self._list[i] in attr
        else:
            for (i,tag) in enumerate(self.tags):
                self.tags[i].attrs['checked'] = tag.attrs['value'] in attr

    def __iter__(self):
        return iter(zip(self._list,self.tags))

def Sum(iterable):
    """Return the concatenation of the instances in the iterable
    Can't use the built-in sum() on non-integers"""
    it = [ item for item in iterable ]
    if it:
        return reduce(lambda x,y:x+y, it)
    else:
        return ''

# whitespace-insensitive tags, determines pretty-print rendering
_LINE_BREAK_AFTER = _NON_CLOSING_TAGS + ['HTML','HEAD','BODY',
    'FRAMESET','FRAME',
    'TITLE','SCRIPT',
    'TABLE','TR','TD','TH','SELECT','OPTION',
    'FORM',
    'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
    'UL','LI','OL'
    ]
# tags whose opening tag should be alone in its line
_ONE_LINE = ['HTML','HEAD','BODY',
    'FRAMESET'
    'SCRIPT',
    'TABLE','TR','TD','TH','SELECT','OPTION',
    'FORM','UL','OL'
    ]

if __name__ == '__main__':
    head = HEAD(TITLE('Test document'))
    body = BODY()
    body <= H1('This is a test document')
    lines = 'First line' + BR() + 'Second line'+DIV(H1("zone"),name="zone")    
    print(type(lines))
    print(lines)
    print('='*77)
    body <= lines

    print('.......... lines.get_by_attr(name="zone")')
    print(lines.get_by_attr(name="zone"))
    print(body.get_by_attr(name="zone"))
    
    print()
    print('.............. for tag in body.get_by_tag("H1"):... print tag')
    for tag in body.get_by_tag("H1"):
        print(tag)

    print("..........HTML(head + body)")
    print(HTML(head + body))

    print(".........TD(B(u'd')+I('a'))*3")
    print(TD(B('d')+I('a'))*3)
    
    formats = ['DEFAULT','DATE (YYYY-MM-DD)',
        'TIME (HH:MM:SS)','TIMESTAMP (YYY-MM-DD HH:MM:SS)']
    sf = SELECT().from_list(formats)
    sf.select(content='TIME (HH:MM:SS)')
    print(sf)
    
    s = SELECT(name="foo",MULTIPLE=True).from_list(['a','b','c','e'])
    s.select(content=['b','e'])
    print(s)
    

    lines = TR(TD("Login")+TD(INPUT(name="login")))
    lines += TR(TD("Password")+TD(INPUT(name="passwd",Type="passwordAO")))
    lines += TR(TD(INPUT(Type="submit",value="Ok"),colspan="2",align="center"))
    print(len(lines.get_by_tag('TD')),"TD tags in line")

    lines.get_by_tag('TD').set_attr(Class="menu")
    print(lines)
    
    style = STYLE("""
#isp_data {
    font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
    width: 100%%;
    border-collapse: collapse;
}

#isp_data td, #isp_data th {
    font-size: 1em;
    border: 1px solid #98bf21;
    padding: 3px 7px 2px 7px;
}

#isp_data th {
    font-size: 1.1em;
    text-align: left;
    padding-top: 5px;
    padding-bottom: 4px;
    background-color: #F5F7FA;
    color: #000000;
}

tbody tr:nth-child(odd) {
    color: #000000;
    background-color: #F5F7FA;
}

tbody tr:nth-child(even) {
    color: #000000;
    background-color: #F5F7FA;
}

.header {
	font-size: 14px;
	color: #A62F24;
	font-weight: bold;
	line-height: 18px;
	margin-bottom: 8px;
}
""")
    print('_'*77)
    print(style)