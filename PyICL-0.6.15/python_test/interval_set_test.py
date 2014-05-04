#
# Copyright John Reid 2011
#

import _pyicl as P

# Construction
P.FloatIntervalSet()
P.FloatIntervalSet(.1)
interval_set = P.FloatIntervalSet(P.FloatInterval(.1, .9))
P.FloatIntervalSet(interval_set)

# Iteration
for interval in P.FloatIntervalSet(P.FloatInterval(.1, .9)):
    str(interval)
assert P.FloatInterval(.1, .9) == P.FloatIntervalSet(P.FloatInterval(.1, .9)).find(.5)

# empty-ness
assert not P.FloatIntervalSet()
assert P.FloatIntervalSet().empty
assert P.FloatIntervalSet(.1)
assert not P.FloatIntervalSet(.1).empty

# containedness
assert .1 in P.FloatIntervalSet(.1)
assert .2 not in P.FloatIntervalSet(.1)
assert .2 in P.FloatIntervalSet(P.FloatInterval(.1, .9))
assert P.FloatInterval(.1, .9) in P.FloatIntervalSet(P.FloatInterval(.1, .9))
assert P.FloatIntervalSet(P.FloatInterval(.1, .9)) in P.FloatIntervalSet(P.FloatInterval(.1, .9))

# Equivalences and Orderings
#print P.IntIntervalSet(1), P.IntIntervalSet(P.IntInterval(1, 1))
assert P.IntIntervalSet(1) == P.IntIntervalSet(1)
#assert P.IntIntervalSet(1) == P.IntIntervalSet(P.IntInterval(1, 1))
assert not P.IntIntervalSet(1) == P.IntIntervalSet(P.IntInterval(1, 3))
assert P.IntIntervalSet(1) != P.IntIntervalSet(P.IntInterval(1, 3))
assert P.IntIntervalSet(1) < P.IntIntervalSet(P.IntInterval(1, 3))
assert not P.IntIntervalSet(1) > P.IntIntervalSet(P.IntInterval(1, 3))

# Size
assert 4 == P.IntIntervalSet(P.IntInterval(1, 5)).size
assert 4 == P.IntIntervalSet(P.IntInterval(1, 5)).cardinality
assert 4 == len(P.IntIntervalSet(P.IntInterval(1, 5)))
assert 1 == P.IntIntervalSet(P.IntInterval(1, 5)).iterative_size
assert 1 == P.IntIntervalSet(P.IntInterval(1, 5)).interval_count

# Range
#    assert 1 == P.IntIntervalSet(P.IntInterval(1, 5)).lower
#    assert 5 == P.IntIntervalSet(P.IntInterval(1, 5)).upper
#    assert 1 == P.IntIntervalSet(P.IntInterval(1, 5)).first
#    assert 4 == P.IntIntervalSet(P.IntInterval(1, 5)).last

# Subtraction
assert P.IntInterval(1, 3) == P.IntInterval(1, 5).right_subtract(P.IntInterval(3, 5))
assert P.IntInterval(3, 5) == P.IntInterval(1, 5).left_subtract(P.IntInterval(1, 3))

# Intersection
assert P.IntInterval(1, 3) == P.IntInterval(1, 5).intersection(P.IntInterval(0, 3))
assert P.IntInterval(1, 3) == P.IntInterval(1, 5) & P.IntInterval(0, 3)
interval = P.IntInterval(1, 5)
interval &= P.IntInterval(0, 3)
assert P.IntInterval(1, 3) == interval 
assert P.IntInterval(3, 5).intersects(P.IntInterval(1, 4))
assert not P.IntInterval(3, 5).intersects(P.IntInterval(1, 3))
assert not P.IntInterval(3, 5).disjoint(P.IntInterval(1, 4))
assert P.IntInterval(3, 5).disjoint(P.IntInterval(1, 3))

assert '[1,5)' == str(P.IntInterval(1, 5))
assert '[1,5)' == str(P.FloatInterval(1, 5))


