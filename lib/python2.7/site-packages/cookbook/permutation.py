#
# Copyright John Reid 2009
#

"""
Code to handle permutations and their inverses.
"""


def identity_permutation(size):
    "@return: The identity permutation."
    return range(size)


def invert_permutation(permutation):
    "@return: The inversion of the permutation."
    result = [None] * len(permutation)
    for i, x in enumerate(permutation):
        result[x] = i
    return result


def chain_permutations(permutation1, permutation2):
    "@return: A permutation that consists of the 2 permutations chained together."
    return [permutation2[p] for p in permutation1]


def permute(x, permutation):
    "@return: A list that is the permuted version of x."
    return list(permute_yield(x, permutation))


def permute_yield(x, permutation):
    "A generator that yields a permuted version of x."
    for p in permutation:
        yield x[p]




if '__main__' == __name__:
    import numpy.random
    size = 10
    permutation = numpy.random.permutation(size)

    def assert_sequences_equal(s1, s2):
        "Assert 2 sequences are identical."
        assert len(s1) == len(s2)
        for x1, x2 in zip(s1, s2):
            assert x1 == x2

    # check chaining inversion results in identity permutation
    assert_sequences_equal(identity_permutation(size), chain_permutations(invert_permutation(permutation), permutation))
    assert_sequences_equal(identity_permutation(size), chain_permutations(permutation, invert_permutation(permutation)))

    # check double inversion is same as permutation
    inversion = invert_permutation(permutation)
    double_inversion = invert_permutation(inversion)
    assert_sequences_equal(permutation, double_inversion)

    # check data permuted correctly
    x = numpy.random.randint(0, 100, size=size)
    permuted = permute(x, permutation)
    for i, p in enumerate(permutation):
        assert x[p] == permuted[i]

    # check inversion of permuted data is correct
    assert_sequences_equal(permute(permuted, inversion), x)
