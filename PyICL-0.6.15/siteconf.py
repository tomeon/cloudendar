BOOST_INC_DIR = ['/usr/local/include/boost']
BOOST_LIB_DIR = ['/usr/local/lib']
BOOST_COMPILER = 'gcc43'
BOOST_PYTHON_LIBNAME = ['boost_python-py27']
CXXFLAGS = ['-I/usr/local/include/python2.7', '-I/usr/local/include']
LDFLAGS = ['-L/usr/local/lib/python2.7', '-L/usr/local/lib', '-lboost_python', '-lpython2.7']
