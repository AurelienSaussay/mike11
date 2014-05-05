from pyparsing import *
from collections import OrderedDict
import json

# Turn the parsed output to JSON

def to_lists(toks):
    if isinstance(toks, ParseResults):
        return [to_lists(t) for t in toks]
    else:
        return toks

def build_dict(toks):
    if isinstance(toks, list):
        if len(toks) == 0:
            return []
        elif len(toks) > 1 and isinstance(toks[0], basestring) and isinstance(toks[1], list):
            return OrderedDict([[toks[0], build_dict(toks[1])]])
        elif isinstance(toks[0], list):
            json = OrderedDict()
            for t in toks:
                json[t[0]] = build_dict(t[1])
            return json
        else:
            return toks
        return []

# Grammar
integer = Combine(Optional('-') + Word(nums)).setParseAction(lambda toks: int(toks[0]))
real =  Combine(Optional('-') + Word(nums) + '.' + Word(nums)).setParseAction(lambda toks: float(toks[0]))
name = Word(alphas, alphanums)
comment = Suppress(dblSlashComment())
le = Suppress(LineEnd())
string = QuotedString("'")
path = QuotedString("|")
bool = Keyword('true') | Keyword('false')
lst = Group(delimitedList(string | path | bool | real | integer))
definition = Group(name + Suppress(Literal('=')) + lst) + Optional(comment)

sectionName = Suppress(Literal('[')) + name + Suppress(Literal(']'))
sectionEnd = Suppress(Keyword('EndSect')) + Optional(comment)
section = Forward()
section << Group(sectionName + Group(ZeroOrMore(section | definition)) + sectionEnd)

mike11 = ZeroOrMore(comment | section).setParseAction(lambda toks: to_lists(toks))

test = open('High_Kelani-Current.bnd11.txt', 'r').read()
#print json.dumps(mike11.parseString(test)[0], indent=2)

# Tests
def tests():
    simpleDefinition = "Inflow = 2, 0, 1, |..\..\..\Colombo_Water_Quality\dfs0\2003Nov_2004Jan.dfs0|, 0.001, 1, 'ZeroDis', 0, 1"
    print definition.parseString(simpleDefinition)

    emptySection = """
    [HDArray]
    EndSect  // HDArray
    """
    print mike11.parseString(emptySection)

    simpleSection = """
    [InflowArray]
    Inflow = 2, 0, 1, |..\..\..\Colombo_Water_Quality\dfs0\2003Nov_2004Jan.dfs0|, 0.001, 1, 'ZeroDis', 0, 1
    EndSect  // InflowArray
    """
    print mike11.parseString(simpleSection)

    multipleLineSection = """
    [ComponentArray]
    Component = 1, 0, 1, ||, 0, 0, '', 0, 1
    Component = 2, 0, 0, |..\..\..\Colombo_Water_Quality\dfs0\Polution_concentrations.dfs0|, 0, 3, 'Non_decay_low', 0, 1
    Component = 3, 0, 0, |..\..\..\Colombo_Water_Quality\dfs0\Polution_concentrations.dfs0|, 0, 6, 'decay_low', 0, 1
    Component = 4, 0, 1, ||, 0, 0, '', 0, 1
    EndSect  // ComponentArray
    """
    print mike11.parseString(multipleLineSection)

    nestedSections = """
    [BndItem]
    [FractionArray]
    EndSect  // FractionArray
    EndSect  // BndItem
    """
    print json.dumps(mike11.parseString(nestedSections)[0])

    complexSection = r"""
    [BndItem]
    DescType = 0, 1, 'Torrington_B01', 0, 0, '', ''
    OpenDesc = 0, 0
    Dam = 0, 0, 0
    Inflow = true, false, false, false
    ADRR = '', 0, 0
    QhADM12 = 2, 1, 0
    AutoCalQh = 0, 0.001, 40
    BndTS = 0, ||, 0, 0, '', 0, 1
    [FractionArray]
    EndSect  // FractionArray

    [HDArray]
    EndSect  // HDArray

    [InflowArray]
    Inflow = 2, 0, 1, |..\..\..\Colombo_Water_Quality\dfs0\2003Nov_2004Jan.dfs0|, 0.001, 1, 'ZeroDis', 0, 1
    EndSect  // InflowArray

    [QhArray]
    EndSect  // QhArray

    [ComponentArray]
    Component = 1, 0, 1, ||, 0, 0, '', 0, 1
    Component = 2, 0, 0, |..\..\..\Colombo_Water_Quality\dfs0\Polution_concentrations.dfs0|, 0, 3, 'Non_decay_low', 0, 1
    Component = 3, 0, 0, |..\..\..\Colombo_Water_Quality\dfs0\Polution_concentrations.dfs0|, 0, 6, 'decay_low', 0, 1
    Component = 4, 0, 1, ||, 0, 0, '', 0, 1
    EndSect  // ComponentArray

    EndSect  // BndItem
    """
    print json.dumps(mike11.parseString(complexSection)[0], indent=2)

    withComments = """
    // Created     : 2013-04-5 9:38:54
    // DLL id      : C:\Program Files (x86)\DHI\2011\Bin\pfs2004.dll
    // PFS version : Jan  6 2011 20:45:15

    [BndCondition]
    Comment = ''
    [BndCndArray]
    EndSect  // ComponentArray
    EndSect  // BndItem
    """
    print mike11.parseString(withComments)

tests()
