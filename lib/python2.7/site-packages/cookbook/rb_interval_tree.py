#
# Copyright John Reid 2009
#



"""
An augmented red-black tree that handles intervals.
"""


from rbtree import rbnode, rbtree, write_tree_as_dot, test_tree
from cookbook.interval import Interval
import logging


class rbintervalnode(rbnode):
    """
    A node of a red black tree of half-open intervals.
    """

    def __init__(self, key):
        "Construct."
        rbnode.__init__(self, key)
        self._max = self._key_max()

    max = property(fget=lambda self: self._max, doc="The maximum value of any endpoint in the subtree rooted at this node.")

    def _key_max(self):
        "@return: The maximum of the key of this node."
        if self.key:
            return self.key.end
        else:
            return None

    def _set_max_locally(self):
        "Use local information (i.e. children) to set max."
        self._max = max(self._key_max(), self.left.max, self.right.max)

    def __str__(self):
        "String representation."
        return '%s; max=%s' % (self.key, self.max)


    def __repr__(self):
        "String representation."
        return '%s; max=%s' % (self.key, self.max)

    def subtree_interval(self):
        "@return: An interval that the subtree rooted here spans."
        return Interval(self.key.start, self.max)





class rbintervaltree(rbtree):
    """
    A red black tree of half-open intervals. See Cormen, Leiserson, Rivest, Stein 2nd edition pg 311.
    """


    def __init__(self):
        "Construct."
        rbtree.__init__(self, create_node=rbintervalnode)


    def interval_search(self, i):
        "Search for a node whose interval overlaps i."
        x = self.root
        while x != self.nil and not i.overlap(x.key):
            if x.left != self.nil and x.left.max > i.start:
                x = x.left
            else:
                x = x.right
        return x


    def _propagate_augmented(self, z):
        "Propagate any changes to the augmented data up the tree."
        z._set_max_locally()
        while z.p != self.nil and z.p.max < z.max:
            z.p._max = max(z.p.max, z.max)
            z = z.p

    def _insert_fixup(self, z):
        "Restore max invariant properties after insert."
        self._propagate_augmented(z)
        rbtree._insert_fixup(self, z)

    def _left_rotate(self, x):
        "Left rotate and keep max values correct."
        rbtree._left_rotate(self, x)
        x.p._max = x.max
        x._set_max_locally()


    def _right_rotate(self, y):
        "Right rotate and keep max values correct."
        rbtree._right_rotate(self, y)
        y.p._max = y.max
        y._set_max_locally()


    def check_invariants(self):
        "Check the max invariant of the nodes and the red-black properties."
        def check_node(x):
            if self.nil == x:
                return x.max == None
            else:
                if x.max != max(x._key_max(), x.left.max, x.right.max):
                    assert False
                    return False
                return check_node(x.left) and check_node(x.right)

        return check_node(self.root) and rbtree.check_invariants(self)



    def find_closest_intervals(self, interval, max_distance=None):
        "@return: The closest intervals in the interval tree to the given interval."
        def visit_node(node, args):
            if None != node.key:
                closest_so_far = args[0]
                closest_distance_so_far = args[1]
                logging.debug(
                    'Looking for closest to %s; visiting %25s; best distance: %4s; closest so far: %s ',
                    interval, node, closest_distance_so_far, closest_so_far
                )

                distance = node.key.separation(interval)
                if abs(distance) < closest_distance_so_far:
                    args[0] = [node.key]
                    args[1] = abs(distance)
                elif abs(distance) == closest_distance_so_far:
                    args[0].append(node.key)

                # do we need to go any further?
                if node.key.start - interval.end <= closest_distance_so_far:
                    visit_node(node.right, args)

                if interval.start - node.max <= args[1]:
                    visit_node(node.left, args)

        if None == max_distance:
            max_distance = float('infinity')
        args = [[], max_distance]
        visit_node(self.root, args)

        return args



if '__main__' == __name__:
    logging.basicConfig(level=logging.DEBUG)
    def write_tree(t, filename):
        "Write the tree as an SVG file."
        f = open('%s.dot' % filename, 'w')
        write_tree_as_dot(t, f)
        f.close()
        os.system('dot %s.dot -Tsvg -o %s.svg' % (filename, filename))

    # test the rbtree
    import os, sys, numpy.random as R
    R.seed(2)
    size=50
    intervals = [Interval(start, start+length) for start, length in zip(R.randint(-5000, 5000, size=size), R.poisson(10., size=size))]
    interval_tree = rbintervaltree()
    test_tree(interval_tree, intervals)
    write_tree(interval_tree, 'interval_tree')
    print interval_tree.find_closest_intervals(Interval(3,30), max_distance=None)
