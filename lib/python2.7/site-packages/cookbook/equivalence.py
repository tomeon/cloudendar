"""From http://code.activestate.com/recipes/499354-equivalence-partition/
"""

def equivalence_partition( iterable, relation ):
    """
    Partitions a set of objects into equivalence classes

    :param iterable:
        collection of objects to be partitioned
    :param relation:
        equivalence relation. I.e. relation(o1,o2) evaluates to True
        if and only if o1 and o2 are equivalent

    :returns: (classes, partitions)
        classes is a sequence of sets. Each one is an equivalence class.
        partitions is a dictionary mapping objects to equivalence classes.
    """
    classes = []
    partitions = { }
    for o in iterable: # for each object
        # find the class it is in
        for c in classes:
            if relation( iter(c).next(), o ): # is it equivalent to this class?
                c.add( o )
                partitions[o] = c
                break
        else: # it is in a new class
            classes.append( set( [ o ] ) )
            partitions[o] = classes[-1]
    return classes, partitions



def equivalence_enumeration( iterable, relation ):
    """Partitions a set of objects into equivalence classes

    Same as equivalence_partition() but also numbers the classes.

    :param iterable: collection of objects to be partitioned
    :param relation: equivalence relation. I.e. relation(o1,o2) evaluates to True
        if and only if o1 and o2 are equivalent

    :returns: (classes, partitions, ids)
        classes is a sequence of sets. Each one is an equivalence class
        partitions is a dictionary mapping objects to equivalence classes
        ids is a dictionary mapping objects to the indices of their equivalence classes
    """
    classes, partitions = equivalence_partition( iterable, relation )
    ids = { }
    for i, c in enumerate( classes ):
        for o in c:
            ids[o] = i
    return classes, partitions, ids

def check_equivalence_partition( classes, partitions, relation ):
    """Checks that a partition is consistent under the relationship"""
    for o, c in partitions.iteritems():
        for _c in classes:
            assert (o in _c) ^ (not _c is c)
    for c1 in classes:
        for o1 in c1:
            for c2 in classes:
                for o2 in c2:
                    assert (c1 is c2) ^ (not relation( o1, o2 ))

def test_equivalence_partition():
    relation = lambda x,y: (x-y) % 4 == 0
    classes, partitions = equivalence_partition(
            xrange( -3, 5 ),
            relation
    )
    check_equivalence_partition( classes, partitions, relation )
    for c in classes: print c
    for o, c in partitions.iteritems(): print o, ':', c
