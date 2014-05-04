#
# Copyright John Reid 2010
#

"""
Code to ease using pytables.
"""


import tables as T
from functools import wraps



def add_to_table(table):
    """
    @return: A decorator that adds arguments and the result of the function to the table.
    """
    def decorator(f):
        """
        A decorator that adds the arguments and result of its argument to a table.
        """
        @wraps(f)
        def wrapper(*args, **kwds):
            "Wrapper function that adds a row of the arguments and the result to a table."
            if kwds:
                raise ValueError('add_to_table decorator cannot handle keyword arguments')
            result = f(*args, **kwds)
            table.append([args + result])
            return result
        return wrapper
    return decorator


def _format_value(table, arg_name, value):
    "@return: The value as a string which may be quoted if necessary."
    if 'string' == table.coltypes[arg_name]:
        return '"%s"' % value
    else:
        return str(value)


def cache_in_table(table, *arg_names):
    """
    @return: A decorator that caches the arguments and the result of the function in the table.
    """
    def decorator(f):
        """
        A decorator that caches the arguments and result of its argument to a table.
        """
        # check arguments are not floats
        for name, t in table.coltypes.iteritems():
            if t.startswith('float'):
                raise ValueError('cache_in_table does not support matching floating point arguments: %s.' % name)
        
        # decorate with add_to_table
        f = add_to_table(table)(f)
        
        @wraps(f)
        def wrapper(*args, **kwds):
            """
            Wrapper function that inspects the table for a matching row and retrieves result or 
            calls function if there is no matching row.
            """
            # check arguments
            if kwds:
                raise ValueError('add_to_table decorator cannot handle keyword arguments')
            if len(args) != len(arg_names):
                raise ValueError('Expecting same number of arguments as names.')
            
            # build a condition to test how many rows we have that match the arguments
            condition = ' & '.join(
                '(%s == %s)' % (arg_name, _format_value(table, arg_name, str(value)))
                for arg_name, value in zip(arg_names, args)
            )
            
            # find the results that match the arguments
            matches = table.getWhereList(condition, condvars={})

            # Either return the existing row in the table or call the function and add a new one.            
            if len(matches) > 1:
                raise ValueError('Got more than one match in table.')
            elif 1 == len(matches):
                # get result from table
                row = table[matches[0]]
            else:
                # call function to get result
                row = f(*args)
            return tuple(row)[len(args):]
        
        return wrapper
    
    return decorator



if '__main__' == __name__:
    
    class TestRow(T.IsDescription):
        str_var     = T.StringCol(16, pos=1)
        int_var     = T.Int64Col(pos=2)
        float_var   = T.Float32Col(pos=3)
        result      = T.Float32Col(pos=4)
    
    #
    # Test the add_to_table decorator by putting some rows in a table
    #
    try:
        h5file
    except NameError:
        h5file = T.openFile("pytables_utils.h5", mode = "a", title = "Test file")
        
    try:
        test_table = h5file.root.Test.test
    except T.NoSuchNodeError:
        test_group = h5file.createGroup("/", 'Test', 'Test group')
        test_table = h5file.createTable(test_group, 'test', TestRow, "Test table")
    
    @add_to_table(test_table)
    def test_add_fn(str_var, int_var, float_var):
        return (len(str_var) * int_var + float_var,)
    
    @cache_in_table(test_table, 'str_var', 'int_var', 'float_var')
    def test_cache_fn(str_var, int_var, float_var):
        return (len(str_var) * int_var + float_var,)
    
#    test_add_fn('AA'  , 1, .5)
#    test_add_fn('AAAA', 2, .6)
#    test_add_fn('CG'  , 3, .7)
    
    test_cache_fn('aa'  , 1, .5)
    test_cache_fn('AAAA', 2, .5)
    test_cache_fn('CG'  , 3, .5)
    
    #
    # Inspect the table to e
    #
    for row in test_table:
        print row

    h5file.close()
    del h5file
    
    
