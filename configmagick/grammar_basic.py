# STDLIB
import pathlib
import re
from typing import List

# EXT
import pypeg2

# OWN
import lib_platform

allowed_chars = r'[\w\^°!§$%&/\(\)\[\]{}\~@\+\-\*\?\>\<\._:`\\]+'
re_allowed_chars = re.compile(allowed_chars)

re_word_with_special_characters = re.compile(r"[\da-zA-Z!§$%&/\\()\[\]{}?*]*\+-_~<>°\^.]*")
re_any_non_whitespace = re.compile(r"[\S+]")
re_double_quoted_string = re.compile(r"\".*\"")
re_single_quoted_string = re.compile(r"\'.*\'")


class GrammarWord(object):
    """ word, containing also special characters like "_" "\" "/" etc...

    >>> import unittest
    >>> assert pypeg2.parse('   test12.!§$%&/\()[]{}?*+-_~<>°^  \\n', GrammarWord).data == 'test12.!§$%&/\\()[]{}?*+-_~<>°^'
    >>> assert pypeg2.parse('   test12%2 \\n', GrammarWord).data == 'test12%2'

    >>> # no separators like , ; |
    >>> unittest.TestCase().assertRaises(Exception, pypeg2.parse, '   a,b \\n', GrammarWord)
    >>> unittest.TestCase().assertRaises(Exception, pypeg2.parse, '   a;b \\n', GrammarWord)

    >>> # no empty field
    >>> unittest.TestCase().assertRaises(Exception, pypeg2.parse, '     \\n', GrammarWord)

    >>> # not quoted
    >>> unittest.TestCase().assertRaises(Exception, pypeg2.parse, '  "abc"   \\n', GrammarWord)
    >>> unittest.TestCase().assertRaises(Exception, pypeg2.parse, "  'abc'   \\n", GrammarWord)

    >>> # compose
    >>> assert pypeg2.compose(GrammarWord('test')) == 'test'
    >>> assert pypeg2.compose(GrammarWord('/test')) == '/test'
    """
    def __init__(self, data=''):
        self.data = data

    grammar = pypeg2.attr('data', re_allowed_chars)


class GrammarQuotedString(object):
    """ single or double quoted String
    >>> assert pypeg2.parse('   "test"  \\n', GrammarQuotedString).data == '"test"'
    >>> assert pypeg2.parse('   ""\\n', GrammarQuotedString).data == '""'
    >>> assert pypeg2.parse("   'test' \\n", GrammarQuotedString).data == "'test'"

    >>> assert pypeg2.parse("   'test und \\'test\\''", GrammarQuotedString).data == "'test und 'test''"
    >>> assert pypeg2.parse("'test'", GrammarQuotedString).data == "'test'"

    >>> # compose
    >>> assert pypeg2.compose(GrammarQuotedString('"test"')) == '"test"'
    >>> assert pypeg2.compose(GrammarQuotedString("'test'")) == "'test'"

    """

    def __init__(self, data=''):
        self.data = data

    grammar = pypeg2.attr('data', [re_single_quoted_string, re_double_quoted_string])


class GrammarKey(object):
    """ for flags
    like :
    ....
    some_flag
    ....

    >>> import unittest
    >>> # test with different characters
    >>> assert pypeg2.parse('   some_flag  \\n', GrammarKey).data == 'some_flag'
    >>> assert pypeg2.parse('   some.flag  \\n', GrammarKey).data == 'some.flag'
    >>> assert pypeg2.parse('   .flag  \\n', GrammarKey).data == '.flag'
    >>> assert pypeg2.parse('   flag.  \\n', GrammarKey).data == 'flag.'
    >>> unittest.TestCase().assertRaises(Exception, pypeg2.parse, '   some_flag  some_flag2\\n', GrammarKey)

    >>> # compose
    >>> assert pypeg2.compose('test') == 'test'

    """

    def __init__(self, data=''):
        self.data = data

    grammar = pypeg2.attr('data', re_allowed_chars)







class GrammarValue(object):
    """ for unquoted or quoted value
    like:
    value
    "value"
    "value with blanks"
    >>> import unittest
    >>> # test with different characters
    >>> pypeg2.parse('   value  \\n', GrammarValue).data

    >>> assert pypeg2.parse('   value  \\n', GrammarValue).data == 'value'
    >>> assert pypeg2.parse('   "value"  \\n', GrammarValue).data == '"value"'
    >>> assert pypeg2.parse('   "value with blanks"  \\n', GrammarValue).data == '"value with blanks"'
    >>> unittest.TestCase().assertRaises(TypeError, pypeg2.parse, '   value  value2\\n', GrammarValue)

    >>> # compose
    >>> assert pypeg2.compose(GrammarValue('test')) == 'test'

    """

    def __init__(self, data=''):
        self.data = GrammarWord(data)

    grammar = pypeg2.attr('data', [GrammarWord, GrammarQuotedString])


class GrammarSingleAssignment(object):
    """ single value assignment :
    like:
    test = value
    test = "value test"

    >>> # normal Case
    >>> result =  pypeg2.parse('   test = test2', GrammarSingleAssignment)
    >>> assert result.key == "test"
    >>> assert result.value == "test2"
    >>> assert result.comment is None

    >>> # quoted Value
    >>> result = pypeg2.parse('test="test2"', GrammarSingleAssignment)
    >>> assert result.key == "test"
    >>> assert result.value == '"test2"'
    >>> assert result.comment is None

    >>> # with comment
    >>> result = pypeg2.parse('test= test3 # some comment', GrammarSingleAssignment)
    >>> assert result.key == "test"
    >>> assert result.value == 'test3'
    >>> assert result.comment == '# some comment'

    >>> # compose
    >>> single_assignment = GrammarSingleAssignment()
    >>> single_assignment.key = GrammarWord('key')
    >>> single_assignment.value = GrammarValue('value')
    >>> single_assignment.comment = pypeg2.comment_sh('# comment')
    >>> pypeg2.compose(single_assignment)


    """

    grammar = pypeg2.attr('key', GrammarKey), '=', pypeg2.attr('value', GrammarValue), pypeg2.attr('comment', pypeg2.optional(pypeg2.comment_sh))


class GrammarMultipleValuesSingleQuotedBlankSeparated(List):
    """ multiple values , quoted, separated by blanks
    used in /etc/updatedb.conf - a very unusual format

    >>> assert pypeg2.parse(" '/tmp /var/spool /media' ", GrammarMultipleValuesSingleQuotedBlankSeparated) == ['/tmp', '/var/spool', '/media']
    >>> assert pypeg2.parse(" '' ", GrammarMultipleValuesSingleQuotedBlankSeparated) == []
    >>> pypeg2.compose(GrammarMultipleValuesSingleQuotedBlankSeparated([GrammarWord('/tmp'), GrammarWord('/var/spool'), GrammarWord('/media')]))
    "'/tmp /var/spool /media'"
    """
    grammar = "'", pypeg2.maybe_some(GrammarWord), "'"


class GrammarMultipleValuesDoubleQuotedBlankSeparated(List):
    """ multiple values , quoted, separated by blanks
    used in /etc/updatedb.conf - a very unusual format

    >>> assert pypeg2.parse(' "/tmp /var/spool /media" ', GrammarMultipleValuesDoubleQuotedBlankSeparated) == ['/tmp', '/var/spool', '/media']
    >>> assert pypeg2.parse(' "" ', GrammarMultipleValuesDoubleQuotedBlankSeparated) == []
    >>> pypeg2.compose(GrammarMultipleValuesDoubleQuotedBlankSeparated([GrammarWord('/tmp'), GrammarWord('/var/spool'), GrammarWord('/media')]))
    '"/tmp /var/spool /media"'
    """
    grammar = '"', pypeg2.maybe_some(GrammarWord), '"'


class GrammarMultipleAssignmentQuotedBlankSeparatedList(List):
    """ multiple values , quoted, separated by blanks
    used in /etc/updatedb.conf - a very unusual format
    >>> test_str = 'PRUNEPATHS="/tmp /var/spool /media"'
    >>> pypeg2.parse(test_str, GrammarMultipleAssignmentQuotedBlankSeparatedList)
    ['PRUNEPATHS', ['/tmp', '/var/spool', '/media']]

    """
    grammar = GrammarKey, '=', [GrammarMultipleValuesSingleQuotedBlankSeparated, GrammarMultipleValuesDoubleQuotedBlankSeparated], pypeg2.optional(pypeg2.comment_sh)


class GrammarConfUpdateDb(List):
    """ multiple values , quoted, separated by blanks
    used in /etc/updatedb.conf - a very unusual format

    >>> if lib_platform.is_platform_linux and pathlib.Path('/etc/updatedb.conf').exists:
    ...     with open('/etc/updatedb.conf', 'r') as conf_file:
    ...        conf_test =   conf_file.read()
    ...     pypeg2.parse(conf_test, GrammarConfUpdateDb)

    """
    grammar = pypeg2.maybe_some([pypeg2.comment_sh, GrammarMultipleAssignmentQuotedBlankSeparatedList])


def test():
    """
    >>> test()

    """
    step1 = GrammarWord('test')
    step2 = pypeg2.compose(GrammarKey(step1))
    pass
