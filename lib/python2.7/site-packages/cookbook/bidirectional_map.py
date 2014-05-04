#
# Copyright John Reid 2008
#



class BidirectionalMap(object):
    """
    A bidirectional map that maintains 2 dicts, one to map each way between elements of type 1 and type 2.

    The map is built by adding pairs of elements that are related.
    """

    def __init__(self):
        from cookbook import DictOfSets

        self.map1 = DictOfSets()
        "Maps from keys of type 1 to values of type 2."

        self.map2 = DictOfSets()
        "Maps from keys of type 2 to values of type 1."


    def add(self, v1, v2):
        """
        Add a relationship between v1 of type 1 and v2 of type 2.
        """
        self.map1[v1].add(v2)
        self.map2[v2].add(v1)


    def remove(self, v1, v2):
        """
        Removed a relationship between v1 of type 1 and v2 of type 2.

        Will throw key error if relationship is not in map.
        """
        self.map1[v1].remove(v2)
        self.map2[v2].remove(v1)


    def discard(self, v1, v2):
        """
        Removed a relationship between v1 of type 1 and v2 of type 2.

        Will do nothing if relationship is not in map.
        """
        self.map1[v1].discard(v2)
        self.map2[v2].discard(v1)
