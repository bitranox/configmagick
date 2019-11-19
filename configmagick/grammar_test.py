
# ext
import pypeg2

# proj
try:
    # imports for local pytest
    from . import grammar_basic         # type: ignore # pragma: no cover
except ImportError:                     # type: ignore # pragma: no cover
    # imports for doctest
    # noinspection PyUnresolvedReferences
    import grammar_basic                # type: ignore # pragma: no cover

def test():
    """
    >>> pypeg2.compose(grammar_basic.GrammarValue(grammar_basic.GrammarWord('test')))

    """
    grammar_basic.GrammarWord.data
    pass
