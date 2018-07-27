"""
Module for various checkers.
"""

import re
import logging
from functools import lru_cache
from abc import ABCMeta, abstractmethod

from .parser import compile_regex
from .exceptions import InvalidPatternError


log = logging.getLogger(__name__)


class RegexChecker:
    """
    Checker that uses regular expressions.
    E.g. 'Dog', 'Doge', 'Dogs' fit <Dog[se]?>
         'Dogger' doesn't fit <Dog[se]?>
    """

    def __init__(self, cache_size=1024):
        """Set up LRU-cache size for compiled regular expressions."""
        self.compile = lru_cache(maxsize=cache_size)(compile_regex)

    def fits(self, policy, field, what):
        """Does Policy fit the given 'what' value by its 'field' property"""
        where = getattr(policy, field, [])
        for i in where:
            # check if 'where' item is not written in a policy-defined-regex syntax.
            if policy.start_tag not in i and policy.end_tag not in i:
                if i != what:
                    continue       # continue if it's not a string match
                else:
                    return True    # we've found a string match - policy fits by simple string value
            try:
                pattern = self.compile(i, policy.start_tag, policy.end_tag)
            except InvalidPatternError:
                log.exception('Error matching policy, because of failed regex %s compilation', i)
                return False
            if re.match(pattern, what):
                return True
        return False


class StringChecker(metaclass=ABCMeta):
    """
    Checker that uses string equality.
    You have to redefine `compare` method.
    """

    def fits(self, policy, field, what):
        """Does Policy fit the given 'what' value by its 'field' property"""
        where = getattr(policy, field, [])
        for item in where:
            if policy.start_tag == item[0] and policy.end_tag == item[-1]:
                item = item[1:-1]
            if self.compare(what, item):
                return True
        return False

    @abstractmethod
    def compare(self, needle, haystack):
        """Compares two string values. Override it in a subclass"""
        pass


class StringExactChecker(StringChecker):
    """
    Checker that uses exact string equality. Case-sensitive.
    E.g. 'sun' in 'sunny' - False
         'sun' in 'sun' - True
    """

    def compare(self, needle, haystack):
        return needle == haystack


class StringFuzzyChecker(StringChecker):
    """
    Checker that uses fuzzy substring equality. Case-sensitive.
    E.g. 'sun' in 'sunny' - True
         'sun' in 'unsung' - True
         'sun' in 'sun' - True
    """

    def compare(self, needle, haystack):
        return needle in haystack
