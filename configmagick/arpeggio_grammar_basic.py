# STDLIB
import pathlib
from typing import List, Union

# EXT
import arpeggio as arp

# PROJ
try:
    # imports for local pytest
    from . import arpeggio_helpers       # type: ignore # pragma: no cover
except ImportError:                      # type: ignore # pragma: no cover
    # imports for doctest
    import arpeggio_helpers              # type: ignore # pragma: no cover


class GrammarBase(object):
    grammar = arp.ParsingExpression()
    whitespace = '\t '

    class Visitor(arp.PTNodeVisitor):
        pass


class GrammarBasic(GrammarBase):
    """
    >>> import unittest

    >>> # newline
    >>> parser = arp.ParserPython(GrammarBasic.newline, ws='\t ')
    >>> assert parser.parse('\\n') == '\\n'

    >>> # double_quoted_string
    >>> parser = arp.ParserPython(GrammarBasic.double_quoted_string)
    >>> assert parser.parse('"double quoted"') == '"double quoted"'
    >>> assert parser.parse('"double \\" quoted"') == '"double " quoted"'
    >>> assert parser.parse('"   test12{öäüß€}.!§$%&/\\()[]{}?*+-_~<>°^"') == '"   test12{öäüß€}.!§$%&/\\()[]{}?*+-_~<>°^"'

    >>> # single_quoted_string
    >>> parser = arp.ParserPython(GrammarBasic.single_quoted_string)
    >>> assert parser.parse("'single quoted'") == "'single quoted'"
    >>> assert parser.parse("'single \\' quoted'") == "'single ' quoted'"
    >>> assert parser.parse("'   test12{öäüß€}.!§$%&/\\()[]{}?*+-_~<>°^'") == "'   test12{öäüß€}.!§$%&/\\()[]{}?*+-_~<>°^'"

    >>> # unicode_string
    >>> parser = arp.ParserPython(GrammarBasic.unicode_string)
    >>> assert parser.parse('unicode_string') == 'unicode_string'
    >>> assert parser.parse('   test12{öäüß€}.!§$%&/\\()[]{}?*+-_~<>°^') == 'test12{öäüß€}.!§$%&/\\()[]{}?*+-_~<>°^'
    >>> unittest.TestCase().assertRaises(arp.NoMatch, parser.parse, '"unicode_string"')
    >>> unittest.TestCase().assertRaises(arp.NoMatch, parser.parse, "'unicode_string'")

    >>> # maybe_quoted_word
    >>> parser = arp.ParserPython(GrammarBasic.maybe_quoted_word)
    >>> assert str(parser.parse('maybe_quoted_word')) == 'maybe_quoted_word'
    >>> assert str(parser.parse("'maybe quoted word single quoted'")) == "'maybe quoted word single quoted'"
    >>> assert str(parser.parse('"maybe quoted word double quoted"')) == '"maybe quoted word double quoted"'
    >>> assert str(parser.parse('"maybe quoted word double quoted" asdf')) == '"maybe quoted word double quoted"'

    >>> # comment_shell
    >>> parser = arp.ParserPython(GrammarBasic.comment_shell)
    >>> assert str(parser.parse('# comment_shell ')) == '# comment_shell '
    >>> assert str(parser.parse('#comment_shell ')) == '#comment_shell '

    >>> # comment_shell_block
    >>> parser = arp.ParserPython(GrammarBasic.comment_shell_block, ws=GrammarBase().whitespace)
    >>> assert str(parser.parse('# comment_shell line1\\n# comment_shell line2\\n')) == '# comment_shell line1 | \\n | # comment_shell line2 | \\n'

    >>> # single_assignment
    >>> parser = arp.ParserPython(GrammarBasic.single_assignment)
    >>> assert str(parser.parse(' single_assignment_key = single_assignment_value # single_assignment_comment ')) ==\
            'single_assignment_key | = | single_assignment_value | # single_assignment_comment '
    >>> assert str(parser.parse(' single_assignment_key = single_assignment_value # single_assignment_comment # comment2')) ==\
            'single_assignment_key | = | single_assignment_value | # single_assignment_comment # comment2'

    >>> # Key
    >>> parser = arp.ParserPython(GrammarBasic.key)
    >>> assert str(parser.parse('key_unicode_string')) == 'key_unicode_string'
    >>> assert str(parser.parse("'key single quoted'")) == "'key single quoted'"
    >>> assert str(parser.parse('"key double quoted"')) == '"key double quoted"'
    >>> assert str(parser.parse('"key double quoted" asdf')) == '"key double quoted"'

    """

    @staticmethod
    def newline():
        return arp.RegExMatch(r"\n")

    @staticmethod
    def double_quoted_string():
        return arp.RegExMatch(r"\".*\"")

    @staticmethod
    class DoubleQuotedString(str):
        def arpeggio_compose(self):
            return '"' + self.replace('"', '\\\\"') + '"'

    @staticmethod
    def single_quoted_string():
        return arp.RegExMatch(r"\'.*\'")

    @staticmethod
    class SingleQuotedString(str):
        def arpeggio_compose(self):
            return "'" + self.replace("'", "\\\\'") + "'"

    @staticmethod
    def allowed_chars():
        return arp.RegExMatch(r'[\w\^°!§$%&/\(\)\[\]{}\~@\+\-\*\?\>\<\._:`\\€]+')

    @staticmethod
    def unicode_string():
        return GrammarBasic.allowed_chars  # to be extended - just for testing now ...

    @staticmethod
    def maybe_quoted_word():
        return arp.OrderedChoice([GrammarBasic.single_quoted_string, GrammarBasic.double_quoted_string, GrammarBasic.unicode_string])

    @staticmethod
    def comment_shell():
        return arp.RegExMatch(r"#.*")

    @staticmethod
    def comment_shell_block():
        return arp.OneOrMore((GrammarBasic.comment_shell, GrammarBasic.newline))

    @staticmethod
    def key():
        return GrammarBasic.maybe_quoted_word

    @staticmethod
    def single_value():
        return GrammarBasic.maybe_quoted_word

    @staticmethod
    def single_assignment():
        return arp.Sequence(GrammarBasic.key, '=', GrammarBasic.single_value, arp.Optional(GrammarBasic.comment_shell))

    @staticmethod
    class Visitor(GrammarBase.Visitor):
        def visit_double_quoted_string(self, node, children):
            value = GrammarBasic.DoubleQuotedString(children[1:-1])
            return value

        def visit_single_quoted_string(self, node, children):
            value = GrammarBasic.SingleQuotedString(children[1:-1])
            return value


class GrammarUpdateDbConf(GrammarBase):
    """
    >>> # multiple_values_quoted
    >>> parser = arp.ParserPython(GrammarUpdateDbConf.assign_multiple_values_quoted, ws=GrammarUpdateDbConf.whitespace)
    >>> assert str(parser.parse('test = "test"\\n')) == 'test | = | " | test | " | \\n'

    >>> assert str(parser.parse('test = "test"\\n')) == 'test | = | \\" | test | \\" | \\n'
    >>> assert str(parser.parse('test = "test1 test2"\\n')) == 'test | = | \\" | test1 | test2 | \\" | \\n'
    >>> assert str(parser.parse('PRUNE_BIND_MOUNTS="yes"\\n')) == 'PRUNE_BIND_MOUNTS | = | \\" | yes | \\" | \\n'
    >>> assert str(parser.parse('PRUNE_BIND_MOUNTS="yes" # test comment  \\n')) == 'PRUNE_BIND_MOUNTS | = | \\" | yes | \\" | # test comment   | \\n'

    >>> # grammar
    >>> parser = arp.ParserPython(GrammarUpdateDbConf.grammar, ws=GrammarUpdateDbConf.whitespace)
    >>> assert str(parser.parse('\\n')) == '\\n | '
    >>> assert str(parser.parse('# test\\n')) == '# test | \\n | '
    >>> assert str(parser.parse('# test\\n# test\\n# test\\n')) == '# test | \\n | # test | \\n | # test | \\n | '
    >>> assert str(parser.parse('PRUNE_BIND_MOUNTS="yes"\\n')) == 'PRUNE_BIND_MOUNTS | = | \\" | yes | \\" | \\n | '
    >>> assert str(parser.parse('PRUNE_BIND_MOUNTS="yes" # test comment\\n')) == 'PRUNE_BIND_MOUNTS | = | \\" | yes | \\" | # test comment | \\n | '
    """

    @staticmethod
    def multiple_values_blank_separated():
        return arp.ZeroOrMore(GrammarBasic.unicode_string)

    @staticmethod
    class MultipleValuesBlankSeparated(list):
        def arpeggio_compose(self):
            composed_elements = arpeggio_helpers.compose_list_elements(self)
            return '"' + ' '.join(composed_elements) + '"'

    @staticmethod
    def assign_multiple_values_quoted():
        return GrammarBasic.key, '=', '"', GrammarUpdateDbConf.multiple_values_blank_separated, '"', arp.Optional(GrammarBasic.comment_shell), GrammarBasic.newline

    @staticmethod
    class AssignMultipleValuesQuoted(list):
        def arpeggio_compose(self):
            composed_elements = arpeggio_helpers.compose_list_elements(self)
            return


    @staticmethod
    def grammar():
        return arp.ZeroOrMore([GrammarUpdateDbConf.assign_multiple_values_quoted, GrammarBasic.comment_shell_block, GrammarBasic.newline]), arp.EOF

    @staticmethod
    class Visitor(GrammarBasic.Visitor):
        def visit_multiple_values_blank_separated(self, node, children):
            return GrammarUpdateDbConf.MultipleValuesBlankSeparated(children)


def read_file(path_file: Union[str, pathlib.Path], grammar: GrammarBase):
    """
    >>> read_file(path_file='/etc/updatedb.conf', grammar=GrammarUpdateDbConf())

    """

    with open(str(path_file), 'r') as data_file:
        string_data = data_file.read()
    parser = arp.ParserPython(grammar.grammar, ws=grammar.whitespace)
    parse_tree = parser.parse(string_data)
    data = arp.visit_parse_tree(parse_tree, grammar.Visitor())
