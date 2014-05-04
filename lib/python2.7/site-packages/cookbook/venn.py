#
# Copyright John Reid 2010
#

"""
Creates Venn diagrams from up to 4 sets.
"""

import numpy as N, scipy.optimize as O, warnings


def mid_points(xs):
    "Calculate mid_points"
    return [(xs[i] + xs[i+1])/2 for i in xrange(len(xs)-1)]

def calc_grid_areas(xs, ys):
    "Calculate the areas given by the grid bounds."
    return N.array(
        [
            [
                (xs[i+1] - xs[i]) * (ys[j+1] - ys[j])
                for i in xrange(len(xs)-1)
            ]
            for j in xrange(len(ys)-1)
        ]
    )


def calc_separation(bounds):
    "@return: A separation value. The closer to 0 it is, the better the bounds will be separated."
    xs = N.sort(bounds[:,:,0].flatten())
    ys = N.sort(bounds[:,:,1].flatten())
    def separation(zs):
        return N.sqrt(sum((zs[i] - zs[i+1])**-2 for i in xrange(len(zs)-1)))
    return separation(xs) + separation(ys)


def calc_squareness(bounds):
    "@return: A square-ness value. The closer to 0 it is, the more square the bounds will be."
    def squareness(bound):
        width = bound[1,0] - bound[0,0]
        height = bound[1,1] - bound[0,1]
        return (width > height and width / height or height / width) - 1
    return N.sqrt((N.array(map(squareness, bounds))**2).sum())


def calc_areas(bounds):
    """
    Calculate the areas given by these bounds.
    """
    assert bounds.shape == (4, 2, 2)
    xs = N.sort(bounds[:,:,0].flatten())
    ys = N.sort(bounds[:,:,1].flatten())
    mid_xs = mid_points(xs)
    mid_ys = mid_points(ys)
    grid_areas = calc_grid_areas(xs, ys)
    areas = N.zeros((2, 2, 2, 2))
    for i, x in enumerate(mid_xs):
        for j, y in enumerate(mid_ys):
            # which sets is it in?
            idx = tuple(b[0,0] < x and x < b[1,0] and b[0,1] < y and y < b[1,1] for b in bounds)
            areas[idx] += grid_areas[i,j]
    areas[0,0,0,0] = 0. # ignore those points outside all sets
    return areas



def calc_error(areas, sizes):
    "Calculate the error associated with these areas."
    assert areas[0,0,0,0] == sizes[0,0,0,0] == 0
    # rescale the areas
    areas = areas * (sizes.sum() / areas.sum())
    return N.sqrt(((areas - sizes)**2).sum())



def fit_venn4(sets):
    """
    Fit a Venn diagram to the 4 sets.
    """
    if 4 != len(sets):
        raise ValueError("Only works with 4 sets.")
    shape = (2, 2, 2, 2)
    sizes = N.zeros(shape, dtype=int) # sizes of all intersections
    union = reduce(set.union, sets)
    print 'Union has %d entries' % len(union)
    for idx in N.ndindex(2, 2, 2, 2):
        intersection = union
        for dim, intersect in enumerate(idx):
            if intersect:
                intersection = intersection.intersection(sets[dim])
            else:
                intersection = intersection.difference(sets[dim])
        sizes[idx] = len(intersection)
    assert sizes[0, 0, 0, 0] == 0
    assert sizes[1, 1, 1, 1] == len(reduce(set.intersection, sets))
    return sizes


def initial_bounds():
    "Return a suitable set of initial bounds."
    return N.array(
        [
            [[0, 0], [4, 6]],
            [[2, 1], [6, 4]],
            [[1, 3], [7, 5]],
            [[3, 2], [5, 7]],
        ],
        dtype=float
    ) / 8.


def find_bounds(sizes):
    """
    Use an optimizer to find the bounds.
    """
    bounds = 100.*initial_bounds().flatten()
    norm_sizes = 100.*sizes/sizes.sum()
    def func(x):
        bounds = x.reshape(4, 2, 2)
        areas = calc_areas(bounds)
        error = calc_error(areas, norm_sizes)
        # add terms to keep edges of sets away from each other
        separation = calc_separation(bounds)
        squareness = calc_squareness(bounds)
        #print error, separation, squareness
        return error + separation / 10. + squareness / 50.
    #xopt, fopt, iter, funcalls, warnflag = O.fmin(func, bounds, full_output=True)
    #xopt, fopt, gopt, Bopt, func_calls, grad_calls, warnflag = O.fmin_bfgs(func, bounds, full_output=True)
    #xopt, fopt, func_calls, grad_calls, warnflag = O.fmin_cg(func, bounds, full_output=True)
    xopt, fopt, direct, iter, funcalls, warnflag = O.fmin_powell(func, bounds, full_output=True)
    if 1 == warnflag:
        warnings.warn('Maximum number of function evaluations made.')
    elif 2 == warnflag:
        warnings.warn('Maximum number of iterations reached.')
    return xopt.reshape(4, 2, 2)/10.


def create_svg(bounds, sizes=None, labels=None, scale=120, font_size=50):
    """
    Create a SVG figure from the bounds.
    """
    import svgfig as S
    fig = S.Fig()
    colors = ["purple", "blue", "green", "yellow"]
    min_x = bounds[:,:,0].min()
    min_y = bounds[:,:,1].min()
    max_x = bounds[:,:,0].max()
    max_y = bounds[:,:,1].max()
    for rect, color in zip(bounds, colors):
        fig.d.append(
            S.SVG(
                "rect",
                x=scale*rect[0,0], y=scale*rect[0,1], width=scale*(rect[1,0]-rect[0,0]), height=scale*(rect[1,1]-rect[0,1]),
                fill=color, fill_opacity=".2",
                rx=10, ry=10,
                stroke_width=2
            )
        )
    if None != labels:
        fig.d.append(S.Text(scale*bounds[0, 0, 0], scale*bounds[0, 0, 1], labels[0], font_size=font_size, text_anchor="start"))
        fig.d.append(S.Text(scale*bounds[1, 1, 0], scale*bounds[1, 0, 1], labels[1], font_size=font_size, text_anchor="end"))
        fig.d.append(S.Text(scale*bounds[2, 1, 0], scale*bounds[2, 1, 1]+font_size, labels[2], font_size=font_size, text_anchor="end"))
        fig.d.append(S.Text(scale*bounds[3, 0, 0], scale*bounds[3, 1, 1]+font_size, labels[3], font_size=font_size, text_anchor="start"))
    return S.canvas(
        fig.SVG(),
        height="800px", width="800px",
        viewBox="%d %d %d %d" % (scale*min_x-font_size, scale*min_y-font_size, scale*(max_x-min_x)+2*font_size, scale*(max_y-min_y)+2*font_size))


if '__main__' == __name__:
    import numpy.random as R
    R.seed(2)

    test_sets = {
        'random' : (
            (
                set(R.randint(0, 1000, 100)),
                set(R.randint(0, 1000, 200)),
                set(R.randint(0, 1000, 300)),
                set(R.randint(0, 1000, 400)),
            ),
            (
                'A - 100',
                'B - 200',
                'C - 300',
                'D - 400',
            )
        ),
        'football' : (
            (
                set('manchester united'),
                set('arsenal'),
                set('liverpool'),
                set('chelsea'),
            ),
            (
                'manchester united',
                'arsenal',
                'liverpool',
                'chelsea',
            )
        )
    }
    for name, (sets, labels) in test_sets.iteritems():
        sizes = fit_venn4(sets)
        bounds = find_bounds(sizes)
        areas = calc_areas(bounds)
        error = calc_error(areas, sizes)
        print 'Final error: %f' % error
        svg = create_svg(bounds, sizes=sizes, labels=labels)
        svg.save('venn-4-%s.svg' % name)
