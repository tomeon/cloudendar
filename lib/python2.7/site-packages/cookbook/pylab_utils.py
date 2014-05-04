#
# Copyright John Reid 2008, 2010
#

"""
Some utilities to use with matplotlib.
"""

import pylab as P, logging, math
from functools import wraps
from contextlib import contextmanager


_logger = logging.getLogger(__name__)

simple_colours = [
    'b',
    'g',
    'r',
    'c',
    'm',
    'y',
    'k',
]
"Basic pylab colours."



@contextmanager
def pylab_context_ioff():
    """A way of turning off pylab's interactive mode with a 'with' statement. For example
    you could do:

        with pylab_context_ioff():
        ... pylab.figure()

    to ensure the figure was created in non-interactive mode. After the context has ended,
    pylab's interactive status is returned to what it was before the context was entered.
    """
    interactive_mode = P.isinteractive()
    if interactive_mode:
        P.ioff()
    try:
        yield
    finally:
        if interactive_mode:
            P.ion()



def pylab_ioff(fn):
    """
    Decorator that turns pylab interactive mode off for duration of call to decorated function.
    """
    @wraps(fn)
    def wrapper(*args, **kwds):
        interactive_mode = P.isinteractive()
        if interactive_mode:
            #logging.debug('Turning pylab interactive off.')
            P.ioff()
        try:
            return fn(*args, **kwds)
        finally:
            if interactive_mode:
                #logging.debug('Turning pylab interactive on.')
                P.ion()

    return wrapper


def set_rcParams_for_latex(fig_width_pt=None):
    """
    Set the rcParams in matplotlib to use postscript output.

    If fig_width_pt is given then set default figure size to match.
    """
    params = {
        'backend'         : 'ps',
        'text.usetex'     : True,
    }
    P.rcParams.update(params)

    if None != fig_width_pt:
        P.rcParams['figure.figsize'] = get_fig_size_for_latex(fig_width_pt)


def get_fig_size_for_latex(fig_width_pt=345.):
    """
    Get fig_width_pt from LaTeX using \showthe\columnwidth

    @return: figure size tuple if fig_width_pt was specified
    """
    inches_per_pt = 1.0/72.27                 # Convert pt to inch
    golden_mean = (math.sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
    fig_width = fig_width_pt * inches_per_pt  # width in inches
    fig_height = fig_width * golden_mean      # height in inches
    return [fig_width, fig_height]



def _choose_other_dim(num_sub_plots, dim):
    return (num_sub_plots - 1) / dim + 1


def layout_sub_plot(num_sub_plots, num_rows=0, num_cols=0):
    "Specify either num_rows or num_cols."

    # make sure are positive
    if num_rows < 0:
        raise ValueError('num_rows must be positive.')
    if num_cols < 0:
        raise ValueError('num_cols must be positive.')

    # are both specified?
    if num_rows and num_cols:
        if (num_rows-1) * num_cols >= num_sub_plots:
            raise ValueError('Specified both num_rows and num_cols but could have used fewer num_rows.')
        if (num_cols-1) * num_rows >= num_sub_plots:
            raise ValueError('Specified both num_rows and num_cols but could have used fewer num_cols.')

    # is num_rows specified?
    elif num_rows:
        num_cols = _choose_other_dim(num_sub_plots, num_rows)

    # is num_cols specified?
    elif num_cols:
        num_rows = _choose_other_dim(num_sub_plots, num_cols)

    # make as square as possible
    else:
        num_rows = int(math.sqrt(num_sub_plots))
        num_cols = _choose_other_dim(num_sub_plots, num_rows)

    return num_rows, num_cols




def violin_plot(ax, data, pos, bp=False, facecolor='y', alpha=0.3):
    '''
    create violin plots on an axis
    '''
    from scipy.stats import gaussian_kde
    from numpy import linspace
    dist = max(pos) - min(pos)
    w = min(0.15 * max(dist, 1.0), 0.5)
    kdes = map(gaussian_kde, data)
    mins = [k.dataset.min() for k in kdes]
    maxs = [k.dataset.max() for k in kdes]
    xs = [linspace(m, M) for m, M in zip(mins, maxs)]
    vs = [k.evaluate(x) for k, x in zip(kdes, xs)]
    scaling = w / max(v.max() for v in vs)
    vs = [v * scaling for v in vs]
    for x, p, v in zip(xs, pos, vs):
        ax.fill_betweenx(x, -v+p,  v+p, facecolor=facecolor, alpha=alpha)
    if bp:
        ax.boxplot(data, notch=1, positions=pos, vert=1)


def create_format_cycler(**formats):
    """Cycle through various format strings so that many different data can be displayed together.

    If specifying many formats it is best to make them relatively prime to ensure the largest total cycle length.
    """
    def get_format_str(i):
        """Get the format string for the i'th data.
        """
        return dict((fmt_name, fmt_values[i % len(fmt_values)]) for fmt_name, fmt_values in formats.iteritems())
    return get_format_str


#
# Create a format cycler
#
all_line_styles = ('-', '--', '-.')
simple_marker_styles = 'vos*D'




if '__main__' == __name__:

    class TestPylabIOff(object):
        @pylab_ioff
        def some_method(self, title, data):
            logging.debug('Plotting')
            P.figure()
            P.plot(data)
            P.title(title)
            P.savefig('test_figure.png')
            P.show()
            P.close()


    @pylab_ioff
    def some_normal_function(title, data):
        logging.debug('Plotting')
        P.figure()
        P.plot(data)
        P.title(title)
        P.savefig('test_other_figure.png')
        P.close()

    logging.basicConfig(level=logging.DEBUG)
    _logger.setLevel(logging.DEBUG)

    P.ion()

    test = TestPylabIOff()
    logging.debug('Trying some_method()')
    test.some_method('Title', [0,1,2,3,4])
    logging.debug('Trying some_normal_function()')
    some_normal_function('Title', [0,1,2,3,4])
