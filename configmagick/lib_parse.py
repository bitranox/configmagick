# STDLIB
import pathlib
from typing import List, Union

# EXT
import arpeggio as arp

# OWN
import lib_path

# PROJ
from . import lib_parse_helpers       # type: ignore # pragma: no cover
from . import grammar_basic           # type: ignore # pragma: no cover


def get_file_semantic(path_file: Union[str, pathlib.Path], grammar: grammar_basic.GrammarBase):
    """ reads the file, parse it and return semantic analyzed data
    >>> test_directory = lib_path.get_test_directory_path(module_name='configmagick', test_directory_name='tests')
    >>> lib_path.make_test_directory_and_subdirs_fully_accessible_by_current_user(test_directory)
    >>> get_file_semantic(path_file=test_directory / 'updatedb.conf', grammar=grammar_basic.GrammarUpdateDbConf())

    """

    with open(str(path_file), 'r') as data_file:
        string_data = data_file.read()
    parse_tree = get_parse_tree(string_data=string_data, grammar=grammar)
    semantic_data = get_semantic_data_from_parse_tree(parse_tree=parse_tree, grammar=grammar)
    return semantic_data


def get_parse_tree(string_data: str, grammar: grammar_basic.GrammarBase):
    """ created the parse tree out of the string
    """
    parser = arp.ParserPython(grammar.grammar, ws=grammar.whitespace)
    parse_tree = parser.parse(string_data)
    return parse_tree


def get_semantic_data_from_parse_tree(parse_tree, grammar: grammar_basic.GrammarBase):
    data = arp.visit_parse_tree(parse_tree, grammar.Visitor())
    return data
