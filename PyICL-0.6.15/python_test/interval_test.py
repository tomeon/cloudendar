#
# Copyright John Reid 2011
#

import _pyicl as P

def test_dynamic_intervals(FloatInterval, IntInterval):
    # empty-ness
    assert not FloatInterval()
    assert FloatInterval().empty
    assert FloatInterval(.1)
    assert not FloatInterval(.1).empty
    assert FloatInterval(.1, .9)
    assert IntInterval(0, 3).touches(IntInterval(3, 5))
    assert not IntInterval(0, 3).touches(IntInterval(2, 5))
    assert not IntInterval(0, 3).touches(IntInterval(4, 5))
    assert not IntInterval(3, 5).touches(IntInterval(0, 3))
    assert 1 == IntInterval(1, 5).first
    assert 4 == IntInterval(1, 5).last
    assert '[1,5)' == str(IntInterval(1, 5))
    assert '[1,5)' == str(FloatInterval(1, 5))
        

def test_intervals(FloatInterval, IntInterval):
    # Construction
    interval = FloatInterval(.1, .9)
    
    # containedness
    #print FloatInterval(1, 5).last
    #print 5 in FloatInterval(1, 5)
    assert 2 in FloatInterval(1, 5)
    assert 6 not in FloatInterval(1, 5)
    assert 2 in IntInterval(1, 5)
    assert 6 not in IntInterval(1, 5)
    assert IntInterval(1, 5) in IntInterval(1, 5)
    assert IntInterval(0, 5) not in IntInterval(1, 5)
    
    # Equivalences and Orderings
    assert IntInterval(1, 3) == IntInterval(1, 3)
    assert IntInterval(1, 3) != IntInterval(5, 6)
    assert not IntInterval(1, 3) != IntInterval(1, 3)
    assert not IntInterval(1, 3) == IntInterval(5, 6)
    assert IntInterval(1, 3) < IntInterval(5, 6)
    assert IntInterval(5, 6) > IntInterval(1, 3)
    assert IntInterval(1, 3) < IntInterval(1, 5)
    assert IntInterval(1, 5) > IntInterval(1, 3)
    assert IntInterval(1, 3) <= IntInterval(5, 6)
    assert IntInterval(5, 6) >= IntInterval(1, 3)
    assert IntInterval(1, 3) <= IntInterval(1, 5)
    assert IntInterval(1, 5) >= IntInterval(1, 3)
    assert not IntInterval(1, 3) > IntInterval(5, 6)
    assert not IntInterval(5, 6) < IntInterval(1, 3)
    assert not IntInterval(1, 3) > IntInterval(1, 5)
    assert not IntInterval(1, 5) < IntInterval(1, 3)
    assert not IntInterval(1, 3).exclusive_less(IntInterval(1, 5))
    assert IntInterval(1, 5).exclusive_less(IntInterval(5, 7))
    assert IntInterval(1, 5).lower_less(IntInterval(2, 7))
    assert not IntInterval(1, 5).lower_less(IntInterval(1, 7))
    assert IntInterval(1, 5).lower_equal(IntInterval(1, 7))
    assert not IntInterval(1, 5).lower_equal(IntInterval(0, 7))
    assert IntInterval(1, 5).lower_less_equal(IntInterval(2, 7))
    assert not IntInterval(1, 5).lower_less_equal(IntInterval(0, 7))
    assert IntInterval(1, 5).upper_less(IntInterval(2, 7))
    assert not IntInterval(1, 5).upper_less(IntInterval(1, 5))
    assert IntInterval(1, 5).upper_equal(IntInterval(1, 5))
    assert not IntInterval(1, 5).upper_equal(IntInterval(0, 7))
    assert IntInterval(1, 5).upper_less_equal(IntInterval(2, 7))
    assert not IntInterval(1, 5).upper_less_equal(IntInterval(0, 3))
    
    # Size
    assert 4 == IntInterval(1, 5).size
    assert 4 == IntInterval(1, 5).cardinality
    assert 4 == len(IntInterval(1, 5))
    assert 4 == len(FloatInterval(1, 5))

    # Range
    assert 1 == IntInterval(1, 5).lower
    assert 5 == IntInterval(1, 5).upper
    
    # Subtraction
    assert IntInterval(1, 3) == IntInterval(1, 5).right_subtract(IntInterval(3, 5))
    assert IntInterval(3, 5) == IntInterval(1, 5).left_subtract(IntInterval(1, 3))
    
    # Intersection
    assert IntInterval(1, 3) == IntInterval(1, 5).intersection(IntInterval(0, 3))
    assert IntInterval(1, 3) == IntInterval(1, 5) & IntInterval(0, 3)
    interval = IntInterval(1, 5)
    interval &= IntInterval(0, 3)
    assert IntInterval(1, 3) == interval 
    assert IntInterval(3, 5).intersects(IntInterval(1, 4))
    assert not IntInterval(3, 5).intersects(IntInterval(1, 3))
    assert not IntInterval(3, 5).disjoint(IntInterval(1, 4))
    assert IntInterval(3, 5).disjoint(IntInterval(1, 3))
    

test_dynamic_intervals(P.FloatInterval, P.IntInterval)
test_intervals(P.FloatInterval, P.IntInterval)
test_intervals(P.FloatIntervalRightOpen, P.IntIntervalRightOpen)
test_intervals(P.FloatIntervalLeftOpen, P.IntIntervalLeftOpen)
