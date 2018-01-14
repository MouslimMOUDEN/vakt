from ..conditions.base import Condition
from ..util import JsonDumper


class StringEqualCondition(Condition, JsonDumper):
    """Condition that is satisfied if the string value equals the specified property of this condition"""

    def __init__(self, equals):
        if not isinstance(equals, str):
            raise TypeError('equals  property should be a string')
        self.equals = equals

    def satisfied(self, what, request):
        return isinstance(what, str) and what == self.equals


class StringPairsEqualCondition(Condition):
    """Condition that is satisfied when given data is an array of pairs and
       those pairs are represented by equal to each other strings"""

    def satisfied(self, what, request):
        if not isinstance(what, list):
            return False
        for pair in what:
            if len(pair) != 2:
                return False
            if not isinstance(pair[0], str) and not isinstance(pair[1], str):
                return False
            if pair[0] != pair[1]:
                return False
        return True
