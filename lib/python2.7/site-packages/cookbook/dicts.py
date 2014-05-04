#
# Copyright John Reid 2007,2008
#


class DictOf(dict):
    "A dictionary where missing values are created by an __init__ time supplied function."

    def __init__(self, missing_value_creator, take_key_as_arg=False):
        "@arg missing_value_creator: Function to create missing values in the dictionary"
        if not take_key_as_arg:
            self.missing_value_creator = lambda k: missing_value_creator()
        else:
            self.missing_value_creator = missing_value_creator

    def __missing__(self, k):
        "Called when there is no value for a given key, k."
        value = self.missing_value_creator(k)
        self[k] = value
        return value


def dict_of(missing_value_creator, take_key_as_arg=False):
    "@return: A function that creates DictOf using these args."
    def result():
        return DictOf(missing_value_creator, take_key_as_arg)
    return result


class DictOfLists(dict):
    """A dictionary where the values are lists. If an accessed key is missing,
    the value is initialised to an empty list"""
    def __missing__(self, k):
        result = self[k] = list()
        return result


class DictOfSets(dict):
    """A dictionary where the values are sets. If an accessed key is missing,
    the value is initialised to an empty set"""
    def __missing__(self, k):
        result = self[k] = set()
        return result


class DictOfDicts(dict):
    """A dictionary where the values are dictionarys. If an accessed key is missing,
    the value is initialised to an empty dict"""
    def __missing__(self, k):
        result = self[k] = dict()
        return result


class DictOfInts(dict):
    """A dictionary where the values are ints. If an accessed key is missing,
    the value is initialised to 0. Useful for counting"""
    def __missing__(self, k):
        self[k] = 0
        return 0


class ChoiceDict(dict):
    """
    Dictionary that assigns one value in a sequence of values to each key. Can be useful for assigning colours/line styles in
    plots for example.
    """

    def __init__(self, values, cycle=False):
        "Construct with given values, if cycle==True then cycle through the values, otherwise raise exception when they are exhausted."
        dict.__init__(self)
        import itertools
        if cycle:
            self.it = itertools.cycle(values)
            "Iterator over values."
        else:
            self.it = iter(values)
            "Iterator over values."

    def __missing__(self, key):
        "Called when key is missing."
        self[key] = self.it.next()
        return self[key]

class UniqueIds(dict):
    """
    Holds a unique integer id for each key that is accessed.
    """

    def __init__(self):
        "Construct."
        self._next_id = 0

    def __missing__(self, key):
        "Called when the key is missing. Creates a new id for the key."
        self[key] = self._next_id
        self._next_id += 1
        return self[key]


if '__main__' == __name__:
    key = 'key'

    lists = DictOfLists()
    lists[key].append(1)
    print 'Should be [1]:', lists[key]

    sets = DictOfSets()
    sets[key].add(1)
    sets[key].add(1)
    print 'Should be set([1]):', sets[key]

    counts = DictOfInts()
    counts[key] += 1
    print 'Should be 1:', counts[key]
