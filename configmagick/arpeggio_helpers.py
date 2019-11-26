# stdlib
from typing import List


def compose_list_elements(elements: List) -> List:
    """ composes the element of a list

    >>> test_object=ComposeTest('xyz')
    >>> test_list = ['a','b','c', test_object]
    >>> assert compose_list_elements(test_list) == ['a', 'b', 'c', 'composed: xyz']

    """
    composed_elements = list()
    for element in elements:
        if hasattr(element, 'arpeggio_compose'):
            composed_elements.append(element.arpeggio_compose())
        else:
            composed_elements.append(element)
    return composed_elements


class ComposeTest(str):
    """
    >>> test_object=ComposeTest('xyz')
    >>> assert test_object == 'xyz'
    >>> assert test_object.arpeggio_compose() == 'composed: xyz'

    """
    def arpeggio_compose(self):
        return 'composed: ' + str(self)
